from django.contrib import admin
from django.contrib.auth.models import User

from content.models import ModelBase


class ModelBaseAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        try:
            obj.owner
        except User.DoesNotExist:
            obj.owner = request.user
      
        obj.save()
            
        """    
        if not obj.owner:
            obj.owner = request.user
            obj.save()
        """
        return super(ModelBaseAdmin, self).save_model(request, obj, form, change)

admin.site.register(ModelBase, ModelBaseAdmin)
