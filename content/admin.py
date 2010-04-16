from django.contrib import admin
from django.contrib.auth.models import User

from content.models import ModelBase

class ModelBaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'state', 'admin_thumbnail', 'owner', 'created')
    list_filter = ('state', 'created')
    search_fields = ('title', 'description', 'state', 'created')
    fieldsets = (
        (None, {'fields': ('state', 'title', 'description', )}),
        ('Meta', {'fields': ('categories', 'tags', 'created', 'owner'),
                    'classes': ('collapse',),
        }),
        ('Image', {'fields': ('image', 'crop_from', 'effect'),
                    'classes': ('collapse',),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.owner:
            obj.owner = request.user
      
        return super(ModelBaseAdmin, self).save_model(request, obj, form, change)
