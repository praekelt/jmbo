from django import template
from django.template import TemplateDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string

register = template.Library()

@register.tag
def render_object(parser, token):
    try:
        tag_name, obj, type = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('render_object tag requires 2 arguments (obj, type), %s given' % (len(token.split_contents()) - 1))
    return RenderObjectNode(obj, type)

class RenderObjectNode(template.Node):
    def __init__(self, obj, type):
        self.obj = template.Variable(obj)
        self.type = type

    def render(self, context):
        obj = self.obj.resolve(context)
        type = self.type

        # generate template name from obj app label, model and type
        obj_type = ContentType.objects.get_for_model(obj)
        template_name = "%s/inclusion_tags/%s_%s.html" % (obj_type.app_label, obj_type.model, type)

        # create response from template. if template is not found for obj type use default content template.
        # if default content template is not found for type return empty response
        try:
            response = render_to_string(template_name, context)
        except TemplateDoesNotExist:
            template_name = "content/inclusion_tags/content_%s.html" % type
            try:
                response = render_to_string(template_name, context)
            except TemplateDoesNotExist:
                response = ''

        return response
