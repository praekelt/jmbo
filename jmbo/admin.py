from copy import deepcopy

from django.db.models.fields import FieldDoesNotExist
from django import forms
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from category.models import Category
from category.admin import CategoryAdmin
from publisher.models import Publisher
from photologue.admin import ImageOverrideInline
from sites_groups.widgets import SitesGroupsWidget

from jmbo.models import ModelBase, Pin, Relation


def make_published(modeladmin, request, queryset):
    queryset.update(state='published')
make_published.short_description = "Mark selected items as published"


def make_staging(modeladmin, request, queryset):
    queryset.update(state='staging')
make_staging.short_description = "Mark selected items as staging"


def make_unpublished(modeladmin, request, queryset):
    queryset.update(state='unpublished')
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

    actions = [make_published, make_staging, make_unpublished]
    inlines = [ImageOverrideInline, ]
    list_display = ('title', 'subtitle', 'state', '_get_absolute_url', \
            'owner', 'created')

    list_filter = ('state', 'created', 'categories',)
    search_fields = ('title', 'description', 'state', 'created')
    fieldsets = (
        (None, {'fields': ('title', 'subtitle', 'description', )}),
        ('Publishing', {'fields': ('state', 'sites', 'publish_on', \
                'retract_on', 'publishers'),
                    'classes': ('collapse',),
        }),
        ('Meta', {'fields': ('categories', 'primary_category', 'tags', \
            'created', 'owner'),
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
