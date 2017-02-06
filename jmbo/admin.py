import os
from copy import deepcopy
from PIL import Image as PILImage

from django import forms
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from category.models import Category
from layers.models import Layer
from photologue.models import PhotoSizeCache
from sites_groups.widgets import SitesGroupsWidget

from jmbo import USE_GIS
from jmbo.models import ModelBase, Relation, Image, ImageOverride
from jmbo.utils import generate_slug


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


def make_published(modeladmin, request, queryset):
    for obj in queryset:
        obj.publish()
make_published.short_description = "Mark selected items as published"


def make_unpublished(modeladmin, request, queryset):
    for obj in queryset:
        obj.unpublish()
make_unpublished.short_description = "Mark selected items as unpublished"


class ImageAdminForm(forms.ModelForm):

    class Meta:
        model = Image
        fields = ("title", "subtitle", "image", "attribution", "crop_from")

    def clean_image(self):
        image = self.cleaned_data['image']
        if image:
            im = PILImage.open(image)
            try:
                im.load()
            except IOError:
                raise forms.ValidationError(
                    "The image is either invalid or unsupported."
                )
        return image


class ImageOverrideInline(admin.TabularInline):
    model = ImageOverride


class ImageAdmin(admin.ModelAdmin):
    form = ImageAdminForm
    list_display = ("title", "_thumb", "_links")
    inlines = (ImageOverrideInline,)

    def _thumb(self, obj):
        return """<img src="%(url)s" />""" % \
            {"url": obj.get_thumbnail_url()}
    _thumb.short_description = _("Thumbnail")
    _thumb.allow_tags = True

    def _links(self, obj):
        s = """<a href="%(url)s">%(url)s</a>
            <br />
            <a href="#"
               onclick="django.jQuery('#jmbo-image-cl-links').toggle(); return false;">
                %(label)s
            </a>
            <ul id="jmbo-image-cl-links" style="display: none;">
            """ % {"url": obj.image.url, "label": _("More / less")}
        for name in sorted(PhotoSizeCache().sizes.keys()):
            s += """<li><a href="%(url)s">%(url)s</a></li>""" % \
                {"url": obj._get_SIZE_url(name)}
        s += "</ul>"
        return s

    _links.short_description = _("Link(s)")
    _links.allow_tags = True


class ModelBaseAdminForm(forms.ModelForm):
    """Helper form for ModelBaseAdmin"""

    class Meta:
        model = ModelBase
        exclude = ('state', 'effect_id', 'primary_category_id', 'owner_id')
        widgets = {'sites': SitesGroupsWidget}

    def __init__(self, *args, **kwargs):
        super(ModelBaseAdminForm, self).__init__(*args, **kwargs)

        # Add relations fields
        content_type = ContentType.objects.get_for_model(self._meta.model)
        relations = Relation.objects.filter(source_content_type=content_type)
        for relation in relations:
            name = relation.name
            if name not in self.fields:
                self.fields[name] = forms.ModelMultipleChoiceField(
                    ModelBase.objects.filter(content_type=relation.target_content_type).order_by('title', 'subtitle'),
                    required=False,
                    label=forms.forms.pretty_name(name),
                )

        instance = kwargs.get('instance', None)
        if instance is not None:
            # Set relations
            for relation in relations:
                name = relation.name
                initial = Relation.objects.filter(
                    source_content_type=instance.content_type,
                    source_object_id=instance.id,
                    name=name
                )
                self.fields[name].initial = [o.target for o in initial]

        if (instance is None) and not self.is_bound:
            # Select all sites initially
            self.fields['sites'].initial = Site.objects.all()

            # Select all layers initially
            self.fields['layers'].initial = Layer.objects.all()

    def clean(self):
        """
        Slug must be unique per site. Show sensible errors when not. Can only
        check in clean method because sites need to be available in
        cleaned_data.
        """

        # Set slug on a clone and do no further validation
        if '_saveasnew' in self.data:
            cleaned_data = self.cleaned_data
            cleaned_data['slug'] = generate_slug(self.instance, cleaned_data['title'])
            return cleaned_data

        slug = self.cleaned_data.get('slug')
        if slug:
            # Check if any combination of slug and site exists.
            for site in self.cleaned_data['sites']:
                q = ModelBase.objects.filter(sites=site, slug=slug)
                if self.instance:
                    q = q.exclude(id=self.instance.id)
                if q.exists():
                    msg = "The slug is already in use by item %s. To use the \
                        same slug the items may not have overlapping \
                        sites." % q[0]
                    self._errors["slug"] = self.error_class([msg])

        return self.cleaned_data


class ImageInline(admin.TabularInline):
    model = ModelBase.images.through


class ModelBaseAdmin(admin.ModelAdmin):
    form = ModelBaseAdminForm
    # ModelBase is typically subclassed so normal app/model/change_form.html
    # based lookups fail in subclasses. Explicitly set the change form
    # template.
    change_form_template = 'admin/jmbo/modelbase/change_form.html'

    actions = (make_published, make_unpublished)
    list_display = ('title', 'subtitle', 'publish_on', 'retract_on', \
        '_get_absolute_url', 'owner', 'created', '_actions'
    )
    inlines = (ImageInline,)

    # The Oracle database adapter is buggy and can't handle sites__sitesgroup
    try:
        has_oracle = 'oracle' in settings.DATABASES['default']['ENGINE']
    except KeyError:
        has_oracle = False
    if has_oracle:
        list_filter = ('state', 'created', CategoriesListFilter)
    else:
        list_filter = ('state', 'created', CategoriesListFilter,
            'sites__sitesgroup', 'sites'
        )

    search_fields = ('title', 'description', 'state', 'created')
    save_as = True
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'subtitle', 'description')}),
        (
            'Publishing',
            {
                'fields': ('sites', 'layers', 'publish_on', 'retract_on'),
                'classes': (),
            }
        ),
        (
            'Metadata',
            {
                'fields': ('categories', 'primary_category', 'tags',
                    'created', 'owner', 'owner_override',
                 ),
                'classes': ('collapse',)
            }
        ),
        (
            'Commenting',
            {
                'fields': ('comments_enabled', 'anonymous_comments',
                    'comments_closed'
                ),
                'classes': ('collapse',)
            }
        ),
        (
            'Liking',
            {
                'fields': ('likes_enabled', 'anonymous_likes', 'likes_closed'),
                'classes': ('collapse',)
            }
        ),
    )
    if USE_GIS:
        fieldsets[3][1]['fields'] = tuple(list(fieldsets[3][1]['fields']) + ['location'])
    prepopulated_fields = {'slug': ('title',)}

    def __init__(self, model, admin_site):
        super(ModelBaseAdmin, self).__init__(model, admin_site)

        fieldsets = deepcopy(self.fieldsets)

        set_fields = []
        for fieldset in self.fieldsets:
            set_fields += fieldset[1]['fields']

        new_fields = []
        for field in model._meta.get_fields():
            name = field.name

            # Don't include through relation if it has more than 3 fields
            try:
                if len(field.rel.through._meta.get_fields()) > 3:
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

        if hasattr(request, "_gfs_marker"):
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
        setattr(request, "_gfs_marker", 1)

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
        if not url:
            return 'N/A'
        result = '<ul>'
        for site in obj.sites.all():
            result += '<li><a href="http://%s%s" target="public">%s</a></li>' % (site.domain, url, site.domain)
        result += '</ul>'
        return result
    _get_absolute_url.short_description = 'Permalink'
    _get_absolute_url.allow_tags = True

    def _actions(self, obj):
        # Deliberately add simple inline javascript here to avoid having to
        # customize change_list.html.
        result = ''
        if obj.state == 'unpublished':
            url = "%s?id=%s" % (reverse('admin:jmbo-publish-ajax'), obj.id)
            result += '''<a href="%s" \
onclick="django.jQuery.get('%s'); django.jQuery(this).replaceWith('Published'); return false;">
Publish</a><br />''' % (url, url)
        if obj.state == 'published':
            url = "%s?id=%s" % (reverse('admin:jmbo-unpublish-ajax'), obj.id)
            result += '''<a href="%s" \
onclick="django.jQuery.get('%s'); django.jQuery(this).replaceWith('Unpublished'); return false;">
Unpublish</a><br />''' % (url, url)
        return result
    _actions.short_description = 'Actions'
    _actions.allow_tags = True

    def publish_ajax(self, request):
        obj = ModelBase.objects.get(id=request.GET["id"])

        if not self.has_change_permission(request, obj):
            return HttpResponseForbidden(
                "You are not allowed to change this object"
            )

        obj.publish()
        return HttpResponse("published")

    def unpublish_ajax(self, request):
        obj = ModelBase.objects.get(id=request.GET["id"])

        if not self.has_change_permission(request, obj):
            return HttpResponseForbidden(
                "You are not allowed to change this object"
            )

        obj.unpublish()
        return HttpResponse("unpublished")

    def autosave_ajax(self, request):
        obj = ModelBase.objects.get(id=request.POST["id"]).as_leaf_class()

        if not self.has_change_permission(request, obj):
            return HttpResponseForbidden(
                "You are not allowed to change this object"
            )

        changes = False
        for field in getattr(obj, "autosave_fields", []):
            new_value = request.POST.get(field)
            old_value = getattr(obj, field)
            if new_value != old_value:
                setattr(obj, field, new_value)
                changes = True
        if changes:
            obj.save()

        return HttpResponse("1")

    def get_urls(self):
        urls = super(ModelBaseAdmin, self).get_urls()
        my_urls = [
            url(
                r'^publish-ajax/$',
                self.admin_site.admin_view(self.publish_ajax),
                name="jmbo-publish-ajax"
            ),
            url(
                r'^unpublish-ajax/$',
                self.admin_site.admin_view(self.unpublish_ajax),
                name="jmbo-unpublish-ajax"
            ),
            url(
                r'^jmbo-autosave-ajax/$',
                self.admin_site.admin_view(self.autosave_ajax),
                name="jmbo-autosave-ajax"
            ),

        ]
        return my_urls + urls


class RelationAdminForm(forms.ModelForm):

    class Meta:
        model = Relation
        fields = (
            'source_content_type', 'source_object_id', 'target_content_type',
            'target_object_id', 'name'
        )

    def __init__(self, *args, **kwargs):
        super(RelationAdminForm, self).__init__(*args, **kwargs)

        # Limit to subclasses of ModelBase
        limit = Q(app_label="_does_not_exist_")
        for ct in ContentType.objects.all():
            model_class = ct.model_class()
            if model_class and (model_class != ModelBase) \
                and issubclass(model_class, ModelBase):
                limit = limit | Q(app_label=ct.app_label, model=ct.model)
        qs = ContentType.objects.filter(limit)
        self.fields["source_content_type"].queryset = qs
        self.fields["target_content_type"].queryset = qs


class RelationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'source_content_type', 'source_object_id', 'target_content_type',
        'target_object_id', 'name'
    )
    form = RelationAdminForm


admin.site.register(Image, ImageAdmin)
admin.site.register(Relation, RelationAdmin)
