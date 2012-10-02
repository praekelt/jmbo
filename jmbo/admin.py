from copy import deepcopy

from django.db.models import Q
from django.db.models.fields import FieldDoesNotExist
from django import forms
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from category.models import Category
from category.admin import CategoryAdmin
from publisher.models import Publisher
from photologue.admin import ImageOverrideInline
from sites_groups.widgets import SitesGroupsWidget

from jmbo.models import ModelBase, Pin, Relation

# Maintain backwards compatibility with Django versions < 1.4.
try:
    from django.contrib.admin import SimpleListFilter

    class CategoriesListFilter(SimpleListFilter):
        title = "categories"
        parameter_name = "category_slug"

        def lookups(self, request, model_admin):
            """
            Returns a list of tuples. The first element in each
            tuple is the coded value for the option that will
            appear in the URL query. The second element is the
            human-readable name for the option that will appear
            in the right sidebar.
            """
            return ((category.slug, category.title) \
                    for category in Category.objects.all())

        def queryset(self, request, queryset):
            """
            Returns queryset filtered on categories and primary_category.
            """
            if self.value():
                category = Category.objects.get(slug=self.value())
                return queryset.filter(Q(primary_category=category) | \
                        Q(categories=category))
except ImportError:
    CategoriesListFilter = 'categories'


def make_published(modeladmin, request, queryset):
    for obj in queryset:
        obj.publish()
make_published.short_description = "Mark selected items as published"


def make_unpublished(modeladmin, request, queryset):
    for obj in queryset:
        obj.unpublish()
make_unpublished.short_description = "Mark selected items as unpublished"


class ModelBaseAdminForm(forms.ModelForm):
    """Helper form for ModelBaseAdmin"""

    class Meta:
        model = ModelBase
        widgets = {'sites': SitesGroupsWidget}

    def __init__(self, *args, **kwargs):
        super(ModelBaseAdminForm, self).__init__(*args, **kwargs)

        # Add relations fields
        content_type = ContentType.objects.get_for_model(self._meta.model)
        relations = Relation.objects.filter(source_content_type=content_type)
        names = set([o.name for o in relations])
        for name in names:
            if name not in self.fields:
                self.fields[name] = forms.ModelMultipleChoiceField(
                    ModelBase.objects.all().order_by('title', 'subtitle'),
                    required=False,
                    label=forms.forms.pretty_name(name),
                    help_text="This field does not perform any validation. \
It is your responsibility to select the correct items."
                )

        instance = kwargs.get('instance', None)
        if instance is not None:
            for name in names:
                initial = Relation.objects.filter(
                    source_content_type=instance.content_type,
                    source_object_id=instance.id,
                    name=name
                )
                self.fields[name].initial = [o.target for o in initial]


class ModelBaseAdmin(admin.ModelAdmin):
    form = ModelBaseAdminForm
    change_form_template = 'admin/jmbo/extras/change_form.html'

    actions = [make_published, make_unpublished]
    inlines = [ImageOverrideInline, ]
    list_display = ('title', 'subtitle', 'publish_on', 'retract_on', \
        '_get_absolute_url', 'owner', 'created', '_actions'
    )

    list_filter = ('state', 'created', CategoriesListFilter,)
    search_fields = ('title', 'description', 'state', 'created')
    fieldsets = (
        (None, {'fields': ('title', 'subtitle', 'description', )}),
        ('Publishing', {'fields': ('sites', 'publish_on', \
                'retract_on', 'publishers'),
                    'classes': ('collapse',),
        }),
        ('Meta', {'fields': ('categories', 'primary_category', 'tags', \
            'created', 'owner', 'location'),
                    'classes': ('collapse',),
        }),
        ('Image', {'fields': ('image', 'crop_from', 'effect'),
                    'classes': (),
        }),
        ('Commenting', {'fields': ('comments_enabled', 'anonymous_comments', \
                'comments_closed'),
                    'classes': ('collapse',),
        }),
        ('Liking', {'fields': ('likes_enabled', 'anonymous_likes', \
                'likes_closed'),
                    'classes': ('collapse',),
        }),
    )

    def __init__(self, model, admin_site):
        super(ModelBaseAdmin, self).__init__(model, admin_site)
        fieldsets = deepcopy(self.fieldsets)

        set_fields = []
        for fieldset in self.fieldsets:
            set_fields += fieldset[1]['fields']

        new_fields = []
        for name in model._meta.get_all_field_names():
            try:
                field = model._meta.get_field(name)
            except FieldDoesNotExist:
                continue

            # don't include custom through relations
            # custom if it has more than 3 fields
            try:
                if len(field.rel.through._meta.get_all_field_names()) > 3:
                    continue
            except AttributeError:
                pass

            if field.editable and field.formfield():
                if name not in set_fields and name not in ['id', ]:
                    new_fields += [name, ]

        for fieldset in fieldsets:
            if fieldset[0] == None:
                fieldset[1]['fields'] += tuple(new_fields)

        self.fieldsets = fieldsets

    def get_fieldsets(self, request, obj=None):
        result = super(ModelBaseAdmin, self).get_fieldsets(request, obj)
        result = list(result)

        content_type = ContentType.objects.get_for_model(self.model)
        q = Relation.objects.filter(source_content_type=content_type)
        if q.exists():
            result.append(
                ('Related',
                    {
                        'fields': set([o.name for o in q]),
                        'classes': ('collapse',),
                    }
                )
            )

        return tuple(result)

    def save_model(self, request, obj, form, change):
        if not obj.owner:
            obj.owner = request.user

        instance = super(ModelBaseAdmin, self).save_model(
            request,
            obj,
            form,
            change
        )

        if hasattr(request, 'POST'):
            if '_save_and_publish' in request.POST:
                obj.publish()
            elif '_save_and_unpublish' in request.POST:
                obj.unpublish()

        content_type = ContentType.objects.get_for_model(self.model)
        relations = Relation.objects.filter(source_content_type=content_type)
        names = set([o.name for o in relations])
        for name in names:
            to_delete = Relation.objects.filter(
                source_content_type=obj.content_type,
                source_object_id=obj.id,
                name=name
            )
            for relation in to_delete:
                relation.delete()
            for target in form.cleaned_data[name]:
                relation = Relation(
                    source=obj, target=target.as_leaf_class(), name=name
                )
                relation.save()

    def _get_absolute_url(self, obj):
        url = obj.get_absolute_url()
        return '<a href="%s" target="public">%s</a>' % (url, url)
    _get_absolute_url.short_description = 'Permalink'
    _get_absolute_url.allow_tags = True

    def _actions(self, obj):
        # Deliberately add simple inline javascript here to avoid having to
        # customize change_list.html.
        result = ''
        if obj.state == 'unpublished':
            url = "%s?id=%s" % (reverse('jmbo-publish-ajax'), obj.id)
            result += '''<a href="%s" \
onclick="django.jQuery.get('%s'); django.jQuery(this).replaceWith('Published'); return false;">
Publish</a><br />''' % (url, url)
        if obj.state == 'published':
            url = "%s?id=%s" % (reverse('jmbo-unpublish-ajax'), obj.id)
            result += '''<a href="%s" \
onclick="django.jQuery.get('%s'); django.jQuery(this).replaceWith('Unpublished'); return false;">
Unpublish</a><br />''' % (url, url)
        return result
    _actions.short_description = 'Actions'
    _actions.allow_tags = True


class PinInline(admin.TabularInline):
    model = Pin


class CategoryJmboAdmin(CategoryAdmin):
    inlines = [
        PinInline,
    ]


class RelationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'source_content_type', 'source_object_id', 'target_content_type',
        'target_object_id', 'name'
    )

try:
    admin.site.register(Category, CategoryJmboAdmin)
except AlreadyRegistered:
    admin.site.unregister(Category)
    admin.site.register(Category, CategoryJmboAdmin)

admin.site.register(Relation, RelationAdmin)
