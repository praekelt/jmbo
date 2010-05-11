from django import template

        
class GenericObjectListTag(template.Node):
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def get_queryset(self):
        raise NotImplementedError('%s should implement get_queryset.' % self.__class__)

    def get_template_name(self):
        raise NotImplementedError('%s should implement get_template_name.' % self.__class__)

    def get_more_url(self):
        raise NotImplementedError('%s should implement get_more_url.' % self.__class__)

    def get_extra_context(self, *args, **kwargs):
        if kwargs.keys():
            return kwargs
        else:
            return None
    
    def render(self, context):
        if not self.queryset:
            self.queryset = self.get_queryset()
        if not self.template_name:
            self.template_name = self.get_template_name()
        if not self.more_url:
            self.more_url = self.get_more_url()
        if not self.extra_context:
            self.extra_context = self.get_extra_context()
        
        context['object_list'] = self.queryset
        context['more_url'] = self.more_url
        context.update(self.extra_context)
        
        return render_to_string(self.template_name, context)
