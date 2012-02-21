from copy import copy

from django import template
from django.template import TemplateDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string

register = template.Library()


@register.inclusion_tag('jmbo/inclusion_tags/content_list_gizmo.html', \
        takes_context=True)
def content_list_gizmo(context, object_list):
    context.update({'object_list': object_list})
    return context


@register.inclusion_tag('jmbo/inclusion_tags/object_comments.html', \
        takes_context=True)
def object_comments(context, obj):
    context.update({
        'object': obj,
        'can_render_comment_form': obj.can_comment(context['request'])
        })
    return context


@register.inclusion_tag('jmbo/inclusion_tags/object_header.html', \
        takes_context=True)
def object_header(context, obj):
    context.update({'object': obj})
    return context


@register.tag
def pager(parser, token):
    """
    Output pagination links.
    """
    try:
        tag_name, page_obj = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            'pager tag requires 1 argument (page_obj), %s given' \
                    % (len(token.split_contents()) - 1)
            )
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
        return render_to_string('jmbo/inclusion_tags/pager.html', context)


@register.tag
def render_object(parser, token):
    try:
        tag_name, obj, type = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            'render_object tag requires 2 arguments (obj, type), %s given' % \
                    (len(token.split_contents()) - 1)
            )
    return RenderObjectNode(obj, type)


class RenderObjectNode(template.Node):
    def __init__(self, obj, type):
        self.obj = template.Variable(obj)
        self.type = template.Variable(type)

    def render(self, context):
        obj = self.obj.resolve(context)
        type = self.type.resolve(context)

        # update context
        context = copy(context)
        context['object'] = obj

        # Generate template name from obj app label, model and type.
        obj_type = ContentType.objects.get_for_model(obj)
        template_name = "%s/inclusion_tags/%s_%s.html" % (obj_type.app_label, \
                obj_type.model, type)
        # Create response from template. if template is not found for obj type
        # use default content template. If default content template is not
        # found for type return empty response.
        try:
            response = render_to_string(template_name, context)
        except TemplateDoesNotExist:
            template_name = "jmbo/inclusion_tags/modelbase_%s.html" % type
            try:
                response = render_to_string(template_name, context)
            except TemplateDoesNotExist:
                response = ''

        return response


@register.tag
def view_modifier(parser, token):
    """
    Output view modifier.
    """
    try:
        tag_name, view_modifier = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            'view_modifier tag requires 1 argument (view_modifier), %s given' \
                    % (len(token.split_contents()) - 1)
            )
    return ViewModifierNode(view_modifier)


class ViewModifierNode(template.Node):
    def __init__(self, view_modifier):
        self.view_modifier = template.Variable(view_modifier)

    def render(self, context):
        view_modifier = self.view_modifier.resolve(context)
        context = {
            'request': context['request'],
            'view_modifier': view_modifier,
        }
        return render_to_string(
            'jmbo/inclusion_tags/view_modifier.html',
            context
        )
