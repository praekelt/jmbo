from django import forms
from django.contrib import admin
from django.contrib.sites.models import Site
from django.contrib.auth.models import User

from content.models import ModelBase
from publisher.models import Publisher

class ModelBaseAdminForm(forms.ModelForm):
    sites = forms.ModelMultipleChoiceField(
        queryset=Site.objects.all(), 
        help_text='Makes item eligible to be published on selected sites.',
        required=False, 
        widget=forms.CheckboxSelectMultiple()
    )
    publishers = forms.ModelMultipleChoiceField(
        queryset=Publisher.objects.all(), 
        help_text='Makes item eligible to be published on selected platform.',
        required=False, 
        widget=forms.CheckboxSelectMultiple())
    class Meta:
        model = ModelBase

class ModelBaseAdmin(admin.ModelAdmin):
    #form = ModelBaseAdminForm

    list_display = ('title', 'state', 'admin_thumbnail', 'owner', 'created')
    list_filter = ('state', 'created')
    search_fields = ('title', 'description', 'state', 'created')
    fieldsets = (
        (None, {'fields': ('title', 'description', )}),
        ('Publishing', {'fields': ('state', 'sites', 'publishers'),
                    'classes': ('collapse',),
        }),
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
