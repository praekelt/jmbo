from django import template
from django.template.loader import render_to_string

register = template.Library()

@register.tag
def filter_menu(parser, token):
    """
    Output filter menu.
    """
    try:
        tag_name, filterset = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('filter_menu tag requires 1 argument (filterset), %s given' % (len(token.split_contents()) - 1))
    return FilterMenuNode(filterset)

class FilterMenuNode(template.Node):
    def __init__(self, filterset):
        self.filterset = template.Variable(filterset)
    
    def render(self, context):
        filterset = self.filterset.resolve(context)
        context = {
            'request': context['request'],
            'filterset': filterset,
        }
        return render_to_string('content/template_tags/filter_menu.html', context)

@register.tag
def pager(parser, token):
    """
    Output pagination links.
    """
    try:
        tag_name, page_obj = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('pager tag requires 1 argument (page_obj), %s given' % (len(token.split_contents()) - 1))
    return PagerNode(page_obj)

class PagerNode(template.Node):
    def __init__(self, page_obj):
        self.page_obj = template.Variable(page_obj)
    
    def render(self, context):
        page_obj = self.page_obj.resolve(context)
        context = {
            'request': context['request'],
            'page_obj': page_obj,
        }
        return render_to_string('content/template_tags/pager.html', context)

@register.tag
def smart_query_string(parser, token):
    """
    Outputs current GET query string with additions appended.
    Additions are provided in token pairs. 
    """
    args = token.split_contents()
    additions = args[1:]
   
    addition_pairs = []
    while additions:
        addition_pairs.append(additions[0:2])
        additions = additions[2:]

    return SmartQueryStringNode(addition_pairs)

class SmartQueryStringNode(template.Node):
    def __init__(self, addition_pairs):
        self.addition_pairs = []
        for key, value in addition_pairs:
            self.addition_pairs.append((template.Variable(key) if key else None, template.Variable(value) if value else None))

    def render(self, context):
        q = dict([(k, v) for k, v in context['request'].GET.items()])
        for key, value in self.addition_pairs:
            if key:
                key = key.resolve(context)
                if value:
                   value = value.resolve(context)
                   q[key] = value
                else:
                    q.pop(key, None)
            qs = '&amp;'.join(['%s=%s' % (k, v) for k, v in q.items()])
        return '?' + qs if len(q) else ''
