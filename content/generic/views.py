from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import loader
from django.template import RequestContext
from django.utils.translation import ugettext
from django.views.generic import list_detail

class DefaultURL(object):
    def __call__(self, obj):
        try:
            return obj.get_absolute_url()
        except AttributeError:
            return ''
    
class GenericObjectList(object):
    def get_pagemenu(self, request, queryset, *args, **kwargs):
        raise NotImplementedError('%s should implement get_pagemenu.' % self.__class__)

    def get_queryset(self, *args, **kwargs):
        raise NotImplementedError('%s should implement get_queryset.' % self.__class__)
    
    def get_pagemenu_altered_queryset(self, queryset, pagemenu):
        if pagemenu:
            return pagemenu.queryset
        else:
            return queryset

    def get_paginate_by(self):
        return None
    
    def get_page(self):
        return None
    
    def get_allow_empty(self):
        return True

    def get_template_name(self):
        return None

    def get_template_loader(self):
        return loader

    def get_url_callable(self):
        return DefaultURL()

    def get_extra_context(self, *args, **kwargs):
        if kwargs.keys():
            return kwargs
        else:
            return None
        
    def get_context_processors(self):
        return None
        
    def get_template_object_name(self):
        return 'object'

    def get_mimetype(self):
        return None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __call__(self, request, *args, **kwargs):
        # get queryset
        queryset = kwargs.get('queryset', getattr(self, 'queryset', self.get_queryset(*args, **kwargs)))
        
        # get pagemenu
        pagemenu = self.get_pagemenu(request, queryset, *args, **kwargs)
        
        # pagemenu altered queryset
        queryset = self.get_pagemenu_altered_queryset(queryset, pagemenu)

        return list_detail.object_list(
            request, 
            queryset=queryset,
            paginate_by=kwargs.get('paginate_by', getattr(self, 'paginate_by', self.get_paginate_by())),
            page=kwargs.get('page', getattr(self, 'page', self.get_page())),
            allow_empty=kwargs.get('allow_empty', getattr(self, 'allow_empty', self.get_allow_empty())),
            template_name=kwargs.get('template_name', getattr(self, 'template_name', self.get_template_name())),
            template_loader=kwargs.get('template_loader', getattr(self, 'template_loader', self.get_template_loader())),
            extra_context=kwargs.get('extra_context', getattr(self, 'extra_context', self.get_extra_context(pagemenu=pagemenu, url_callable=self.get_url_callable, *args, **kwargs))),
            context_processors=kwargs.get('context_processors', getattr(self, 'context_processors', self.get_context_processors())),
            template_object_name=kwargs.get('template_object_name', getattr(self, 'template_object_name', self.get_template_object_name())),
            mimetype=kwargs.get('mimetype', getattr(self, 'mimetype', self.get_mimetype())),
        )

class GenericObjectDetail(object):
    def get_pagemenu(self, request, queryset, *args, **kwargs):
        raise NotImplementedError('%s should implement get_pagemenu.' % self.__class__)

    def get_queryset(self, *args, **kwargs):
        raise NotImplementedError('%s should impliment get_queryset.' % self.__class__)
    
    def get_object_id(self):
        return None
    
    def get_slug(self):
        return None
    
    def get_slug_field(self):
        return 'slug'
    
    def get_template_name(self):
        return None
    
    def get_template_name_field(self):
        return None
    
    def get_extra_context(self, *args, **kwargs):
        if kwargs.keys():
            return kwargs
        else:
            return None
        
    def get_context_processors(self):
        return None
        
    def get_template_object_name(self):
        return 'object'

    def get_mimetype(self):
        return None

    def __call__(self, request, *args, **kwargs):
        # get queryset
        queryset = kwargs.get('queryset', getattr(self, 'queryset', self.get_queryset(*args, **kwargs)))
        
        # get pagemenu
        pagemenu = self.get_pagemenu(request, queryset, *args, **kwargs)
        
        return list_detail.object_detail(
            request,
            queryset=queryset,
            object_id=kwargs.get('object_id', getattr(self, 'object_id', self.get_object_id())),
            slug=kwargs.get('slug', getattr(self, 'slug', self.get_slug())),
            slug_field=kwargs.get('slug_field', getattr(self, 'slug_field', self.get_slug_field())),
            template_name=kwargs.get('template_name', getattr(self, 'template_name', self.get_template_name())),
            template_name_field=kwargs.get('template_name_field', getattr(self, 'template_name_field', self.get_template_name_field())),
            extra_context=kwargs.get('extra_context', getattr(self, 'extra_context', self.get_extra_context(pagemenu=pagemenu, *args, **kwargs))),
            context_processors=kwargs.get('context_processors', getattr(self, 'context_processors', self.get_context_processors())),
            template_object_name=kwargs.get('template_object_name', getattr(self, 'template_object_name', self.get_template_object_name())),
            mimetype=kwargs.get('mimetype', getattr(self, 'mimetype', self.get_mimetype())),
        )

class GenericForm(object):
    def get_pagemenu(self, request, *args, **kwargs):
        raise NotImplementedError('%s should implement get_pagemenu.' % self.__class__)
        
    def get_form_class(self, *args, **kwargs):
        raise NotImplementedError('%s should implement get_form_class.' % self.__class__)
    
    def get_form_args(self, *args, **kwargs):
        return {}

    def handle_valid(self, *args, **kwargs):
        raise NotImplementedError('%s should implement handle_valid.' % self.__class__)
    
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
        raise NotImplementedError('%s should implement redirect.' % self.__class__)
    
    def __call__(self, request, *args, **kwargs):
        form_class = kwargs.get('form_class', getattr(self, 'form_class', self.get_form_class()))
        form_args = kwargs.get('form_args', getattr(self, 'form_args', self.get_form_args(*args, **kwargs)))
        template_name=kwargs.get('template_name', getattr(self, 'template_name', self.get_template_name()))
        pagemenu = kwargs.get('pagemenu', getattr(self, 'pagemenu', self.get_pagemenu(request, *args, **kwargs)))
        success_message = kwargs.get('success_message', getattr(self, 'success_message', self.get_success_message(*args, **kwargs)))

        if request.method == 'POST':
            form = form_class(data=request.POST, files=request.FILES, **form_args)
            if form.is_valid():
                self.handle_valid(form=form, *args, **kwargs)
                msg = ugettext(success_message)
                messages.success(request, msg, fail_silently=True)
                return self.redirect(request, *args, **kwargs)
        else:
            form = form_class(initial=self.get_initial(*args, **kwargs), **form_args)
       
        c = RequestContext(request, {
            'form': form,
            'pagemenu': pagemenu,
        })
        return render_to_response(template_name, c)
