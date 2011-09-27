from copy import deepcopy

from django.db.models.fields import FieldDoesNotExist
from django import forms
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from jmbo.models import ModelBase, Pin

from category.models import Category
from category.admin import CategoryAdmin
from publisher.models import Publisher
from photologue.admin import ImageOverrideInline


def make_published(modeladmin, request, queryset):
    queryset.update(state='published')
make_published.short_description = "Mark selected items as published"


def make_staging(modeladmin, request, queryset):
    queryset.update(state='staging')
make_staging.short_description = "Mark selected items as staging"


def make_unpublished(modeladmin, request, queryset):
    queryset.update(state='unpublished')
make_unpublished.short_description = "Mark selected items as unpublished"


class ModelBaseAdmin(admin.ModelAdmin):
    actions = [make_published, make_staging, make_unpublished]
    inlines = [ImageOverrideInline, ]
    list_display = ('title', 'state', 'admin_thumbnail', 'owner', 'created')
    list_filter = ('state', 'created')
    search_fields = ('title', 'description', 'state', 'created')
    fieldsets = (
        (None, {'fields': ('title', 'description', )}),
        ('Publishing', {'fields': (('state', 'sites'), ('publish_on', 'retract_on'), \
                'publishers'),
                    'classes': ('collapse',),
        }),
        ('Meta', {'fields': ('categories', 'primary_category', 'tags', 'created', 'owner'),
                    'classes': ('collapse',),
        }),
        ('Image', {'fields': ('image', 'crop_from', 'effect'),
                    'classes': ('collapse',),
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

    def save_model(self, request, obj, form, change):
        if not obj.owner:
            obj.owner = request.user

        return super(ModelBaseAdmin, self).save_model(
            request,
            obj,
            form,
            change
        )


class PinInline(admin.TabularInline):
    model = Pin


class CategoryJmboAdmin(CategoryAdmin):
    inlines = [
        PinInline,
    ]


try:
    admin.site.register(Category, CategoryJmboAdmin)
except AlreadyRegistered:
    admin.site.unregister(Category)
    admin.site.register(Category, CategoryJmboAdmin)

