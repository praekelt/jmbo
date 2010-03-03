# python imports
from copy import deepcopy

# django imports
from django.contrib import admin

# our own app imports
from publisher.admin import PublisherAdmin
class ModelBaseAdmin(PublisherAdmin):
    pass

class ContentBaseAdmin(ModelBaseAdmin):
    list_display = ('title', 'owner', 'created', 'modified', 'admin_thumbnail') + PublisherAdmin.list_display
    list_filter = ('created', 'modified',) + PublisherAdmin.list_filter
    search_fields = ('title', 'description')
   
    fieldsets = list(deepcopy(ModelBaseAdmin.fieldsets))
    fieldsets.insert(0, 
        (None, {
            'fields': ('title', 'description', 'tags')
        }))

    fieldsets += ( 
        ('Meta', {
            'fields': ('created', 'owner', 'rating',),
            'classes': ('collapse',),
        }),
        ('Image', {
            'fields': ('image', 'crop_from', 'effect',),
            'classes': ('collapse',),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.owner:
            obj.owner = request.user
            obj.save()
        return super(ContentBaseAdmin, self).save_model(request, obj, form, change)
