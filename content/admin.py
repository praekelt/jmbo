from copy import deepcopy

from django.contrib import admin

class ModelBaseAdmin(admin.ModelAdmin):
    list_display = ('is_public',)
    list_filter = ('is_public',)
    fieldsets = (
        (None, {'fields': ('is_public',)}),
    )

class ContentBaseAdmin(ModelBaseAdmin):
    list_display = ('title', 'owner', 'created', 'modified', 'admin_thumbnail') + ModelBaseAdmin.list_display
    list_filter = ('created', 'modified',) + ModelBaseAdmin.list_filter
    search_fields = ('title', 'description')
   
    fieldsets = deepcopy(ModelBaseAdmin.fieldsets)
    for fieldset in fieldsets:
        if fieldset[0] == None:
            fieldset[1]['fields'] += ('title', 'description',)

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
