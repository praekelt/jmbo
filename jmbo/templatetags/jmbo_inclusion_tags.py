import warnings

from django.db import models
from django import template
from django.template import TemplateDoesNotExist
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.conf import settings


register = template.Library()


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
        # Fallback handling because object_* tags now defer to render_object
        try:
            type = self.type.resolve(context)
        except template.VariableDoesNotExist:
            type = self.type

        # Update context
        context.push()
        context['object'] = obj

        # Template names follow typical Django naming convention, but also
        # traverse upwards over inheritance hierarchy.
        template_names = []
        ct = obj.content_type
        kls = ct.model_class()
        while ct.model != "model":
            template_names.extend((
                "%s/inclusion_tags/%s_%s.html" % \
                    (ct.app_label, ct.model, type),
                "%s/inclusion_tags/modelbase_%s.html" % \
                    (ct.app_label, type),
            ))
            kls = kls.__bases__[0]
            if kls == models.Model:
                break
            ct = ContentType.objects.get_for_model(kls)

        rendered = False
        for template_name in template_names:
            try:
                response = render_to_string(template_name, context.flatten())
                rendered = True
                break
            except TemplateDoesNotExist:
                pass

        context.pop()

        if not rendered:
            if settings.TEMPLATES[0]["OPTIONS"].get("debug", False):
                raise TemplateDoesNotExist({
                    'content_type': ct.app_label,
                    'model': ct.model,
                    'type': type
                })
            else:
                response = ''

        return response


@register.tag
def object_header(parser, token):
    try:
        tag_name, obj = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            'object_header tag requires 1 argument obj, %s given' % \
                    (len(token.split_contents()) - 1)
            )
    return RenderObjectNode(obj, 'header')


@register.tag
def object_footer(parser, token):
    try:
        tag_name, obj = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            'object_footer tag requires 1 argument obj, %s given' % \
                    (len(token.split_contents()) - 1)
            )
    return RenderObjectNode(obj, 'footer')


@register.tag
def object_comments(parser, token):
    try:
        tag_name, obj = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            'object_comments tag requires 1 argument obj, %s given' % \
                    (len(token.split_contents()) - 1)
            )
    return RenderObjectCommentsNode(obj, 'comments')


class RenderObjectCommentsNode(RenderObjectNode):

    def render(self, context):
        obj = self.obj.resolve(context)
        can_comment, code = obj.can_comment(context['request'])
        context.update({
            'object': obj,
            'can_render_comment_form': can_comment,
            'can_comment_code': code
        })
        return super(RenderObjectCommentsNode, self).render(context)


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


@register.tag
def image_url(parser, token):
    """Return image URL for a certain photosize. Defers to _get_image_url in
    order to consider inheritance hierarchy."""

    try:
        tag_name, obj, type = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "image_url tag requires 2 arguments (obj, type), %s given" % \
                    (len(token.split_contents()) - 1)
            )
    return ImageUrlNode(obj, type)


class ImageUrlNode(template.Node):

    def __init__(self, obj, type):
        self.obj = template.Variable(obj)
        self.type = template.Variable(type)

    def render(self, context):
        obj = self.obj.resolve(context)
        type = self.type.resolve(context)
        return obj._get_image_url(type)
