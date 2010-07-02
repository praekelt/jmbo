import copy
import traceback

from django.db.models import Q
from django.db.models.fields import related 
from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import loader
from django.template import RequestContext
from django.utils.translation import ugettext
from django.views.generic import list_detail

class DefaultURL(object):
    def __call__(self, obj=None):
        if obj:
            try:
                return obj.get_absolute_url()
            except AttributeError:
                return ''
        else:
            return self
    
class GenericBase(object):
    def __init__(self, *args, **kwargs):
        self.params=kwargs
        self.params['view_modifier'] = None
        self.params['url_callable'] = None

    def __call__(self, request, *args, **kwargs):
        view = copy.copy(self)
        
        # setup view params
        view.params = view._resolve_view_params(request, view.defaults, *args, **kwargs)
       
        # push the view through view modifier
        if view.params['extra_context'].has_key('view_modifier'):
            view_modifier = view.params['extra_context']['view_modifier']
            if view_modifier:
                view = view_modifier.modify(view)

        return view

    def get_url_callable(self, *args, **kwargs):
        return DefaultURL()

    def _resolve_view_params(self, request, defaults, *args, **kwargs):
        params = copy.copy(defaults)
        params.update(self.params)
        params.update(kwargs)
        resolved_params = {}
        
        extra_context = {}
        for key in params:
            # grab from class method
            value = getattr(self, 'get_%s' % key)(request, *args, **kwargs) if getattr(self, 'get_%s' % key, None) else None

            # otherwise grab from existing params
            if value == None:
                value = self.params[key] if self.params.has_key(key) else None
            
            # otherwise grab from provided params
            if value == None:
                value = params[key]

            if key in defaults:
                resolved_params[key] = value
            else:
                extra_context[key] = value
        
        if extra_context:
            try:
                resolved_params['extra_context'].update(extra_context)
            except AttributeError:
                resolved_params['extra_context'] = extra_context

        return resolved_params
        
class GenericObjectList(GenericBase):
    defaults = {
        'queryset': None,
        'paginate_by': None, 
        'page':None,
        'allow_empty':True, 
        'template_name':None, 
        'template_loader':loader,
        'extra_context':None, 
        'context_processors':None, 
        'template_object_name':'object',
        'mimetype':None,
    }
    
    def __call__(self, request, *args, **kwargs):
        # generate our view via genericbase
        view = super(GenericObjectList, self).__call__(request, *args, **kwargs)
        
        # setup object_list params
        queryset=view.params['queryset']
        del view.params['queryset']

        # return object list generic view
        return list_detail.object_list(request, queryset=queryset, **view.params)
        
generic_object_list = GenericObjectList()
        
class GenericObjectFilterList(GenericObjectList):
    
    def __call__(self, request, *args, **kwargs):
        # generate our view via genericbase
        view = super(GenericObjectList, self).__call__(request, *args, **kwargs)

        # setup object_list params
        queryset=view.params['queryset']
        del view.params['queryset']
        
        # Filter
        for field in queryset.model._meta.fields:
            if field.name in view.params['extra_context'].keys():
                queryset = queryset.filter(Q(**{"%s__exact" % field.name : view.params['extra_context'][field.name]}))
        
        # return object list generic view
        return list_detail.object_list(request, queryset=queryset, **view.params)
        
generic_object_filter_list = GenericObjectFilterList()

class GenericObjectDetail(GenericBase):
    defaults = {
        'queryset': None,
        'object_id': None, 
        'slug': None,
        'slug_field':'slug', 
        'template_name_field':None,
        'template_name':None, 
        'template_loader':loader,
        'extra_context':None, 
        'context_processors':None, 
        'template_object_name':'object',
        'mimetype':None,
    }
    
    def __call__(self, request, *args, **kwargs):
        # generate our view via genericbase
        view = super(GenericObjectDetail, self).__call__(request, *args, **kwargs)
        
        # setup object_list params
        queryset=view.params['queryset']
        del view.params['queryset']

        # return object list generic view
        return list_detail.object_detail(request, queryset=queryset, **view.params)
        
generic_object_detail = GenericObjectDetail()

class GenericForm(object):
    def get_pagemenu(self, request, *args, **kwargs):
        return None
        
    def get_form_class(self, *args, **kwargs):
        return None
    
    def get_form_args(self, *args, **kwargs):
        return {}

    def handle_valid(self, form=None, *args, **kwargs):
        # we take a chance and try save a subclass of a ModelForm.
        if hasattr(form, 'save'):
            form.save(*args, **kwargs)
   
    def get_initial(self, *args, **kwargs):
        return None

    def get_extra_context(self, *args, **kwargs):
        if kwargs.keys():
            return kwargs
        else:
            return None
    
    def get_template_name(self):
        return None

    def redirect(self, request, *args, **kwargs):
        form = self.form_class(initial=self.get_initial(request=request, *args, **kwargs), **self.form_args)
        c = RequestContext(request, {
            'form': form,
            'success_message': self.success_message,
            'pagemenu': self.pagemenu,
        })
        return render_to_response(self.template_name, c)
        
    def get_success_message(self, *args, **kwargs):
        return None
    
    def __call__(self, request, *args, **kwargs):
        self.request = request
        self.form_class = kwargs.get('form_class', getattr(self, 'form_class', self.get_form_class()))
        self.form_args = kwargs.get('form_args', getattr(self, 'form_args', self.get_form_args(*args, **kwargs)))
        self.template_name=kwargs.get('template_name', getattr(self, 'template_name', self.get_template_name()))
        self.pagemenu = kwargs.get('pagemenu', getattr(self, 'pagemenu', self.get_pagemenu(request, *args, **kwargs)))
        self.success_message = kwargs.get('success_message', getattr(self, 'success_message', self.get_success_message(*args, **kwargs)))

        if request.method == 'POST':
            form = self.form_class(data=request.POST, files=request.FILES, **self.form_args)
            if form.is_valid():
                self.handle_valid(form=form, request=request, *args, **kwargs)
                if self.success_message:
                    msg = ugettext(self.success_message)
                    messages.success(request, msg, fail_silently=True)
                return self.redirect(request, *args, **kwargs)
        else:
            form = self.form_class(initial=self.get_initial(request=request, *args, **kwargs), **self.form_args)
      
        context = RequestContext(request, {})
        context.update({
            'form': form,
            'pagemenu': self.pagemenu,
        })
        return render_to_response(self.template_name, context)

generic_form_view = GenericForm()
