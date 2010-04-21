from django.template import loader
from django.views.generic import list_detail

class GenericObjectList(object):
    def get_queryset(self):
        raise NotImplementedError('%s should impliment get_queryset.' % self.__class__)

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

    def get_extra_context(self):
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
        return list_detail.object_list(
            request, 
            queryset=kwargs.get('queryset', getattr(self, 'queryset', self.get_queryset())),
            paginate_by=kwargs.get('paginate_by', getattr(self, 'paginate_by', self.get_paginate_by())),
            page=kwargs.get('page', getattr(self, 'page', self.get_page())),
            allow_empty=kwargs.get('allow_empty', getattr(self, 'allow_empty', self.get_allow_empty())),
            template_name=kwargs.get('template_name', getattr(self, 'template_name', self.get_template_name())),
            template_loader=kwargs.get('template_loader', getattr(self, 'template_loader', self.get_template_loader())),
            extra_context=kwargs.get('extra_context', getattr(self, 'extra_context', self.get_extra_context())),
            context_processors=kwargs.get('context_processors', getattr(self, 'context_processors', self.get_context_processors())),
            template_object_name=kwargs.get('template_object_name', getattr(self, 'template_object_name', self.get_template_object_name())),
            mimetype=kwargs.get('mimetype', getattr(self, 'mimetype', self.get_mimetype())),
        )


class GenericObjectDetail(object):
    def get_queryset(self):
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
    
    def get_extra_context(self):
        return None
        
    def get_context_processors(self):
        return None
        
    def get_template_object_name(self):
        return 'object'

    def get_mimetype(self):
        return None

    def __call__(self, request, *args, **kwargs):
        return list_detail.object_detail(
            request,
            queryset=kwargs.get('queryset', getattr(self, 'queryset', self.get_queryset())),
            object_id=kwargs.get('object_id', getattr(self, 'object_id', self.get_object_id())),
            slug=kwargs.get('slug', getattr(self, 'slug', self.get_slug())),
            slug_field=kwargs.get('slug_field', getattr(self, 'slug_field', self.get_slug_field())),
            template_name=kwargs.get('template_name', getattr(self, 'template_name', self.get_template_name())),
            template_name_field=kwargs.get('template_name_field', getattr(self, 'template_name_field', self.get_template_name_field())),
            extra_context=kwargs.get('extra_context', getattr(self, 'extra_context', self.get_extra_context())),
            context_processors=kwargs.get('context_processors', getattr(self, 'context_processors', self.get_context_processors())),
            template_object_name=kwargs.get('template_object_name', getattr(self, 'template_object_name', self.get_template_object_name())),
            mimetype=kwargs.get('mimetype', getattr(self, 'mimetype', self.get_mimetype())),
        )
