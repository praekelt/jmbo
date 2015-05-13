from copy import copy
from inspect import getargspec
from functools import partial

from django import template
from django.template import TemplateDoesNotExist
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.template.context import Context
from django.template import Node, generic_tag_compiler, Variable
from django.template.base import Template, TagHelperNode
from django.utils.functional import curry
from django.utils.itercompat import is_iterable


register = template.Library()


# Base the inclusion_tag decorator on Django's default register tag. We want
# to be able to dynamically compute a list of templates suitable for rendering.
def inclusion_tag(register, context_class=Context, takes_context=False, name=None):
    def dec(func):
        params, varargs, varkw, defaults = getargspec(func)

        class InclusionNode(TagHelperNode):

            def render(self, context):
                resolved_args, resolved_kwargs = self.get_resolved_arguments(context)

                # Only this line has been changed from the default
                # register_tag
                file_name, _dict = func(*resolved_args, **resolved_kwargs)

                if not getattr(self, 'nodelist', False):
                    from django.template.loader import get_template, select_template
                    if isinstance(file_name, Template):
                        t = file_name
                    elif not isinstance(file_name, basestring) and is_iterable(file_name):
                        t = select_template(file_name)
                    else:
                        t = get_template(file_name)
                    self.nodelist = t.nodelist
                new_context = context_class(_dict, **{
                    'autoescape': context.autoescape,
                    'current_app': context.current_app,
                    'use_l10n': context.use_l10n,
                    'use_tz': context.use_tz,
                })
                # Copy across the CSRF token, if present, because
                # inclusion tags are often used for forms, and we need
                # instructions for using CSRF protection to be as simple
                # as possible.
                csrf_token = context.get('csrf_token', None)
                if csrf_token is not None:
                    new_context['csrf_token'] = csrf_token
                return self.nodelist.render(new_context)

        function_name = (name or
            getattr(func, '_decorated_function', func).__name__)
        compile_func = partial(generic_tag_compiler,
            params=params, varargs=varargs, varkw=varkw,
            defaults=defaults, name=function_name,
            takes_context=takes_context, node_class=InclusionNode)
        compile_func.__doc__ = func.__doc__
        register.tag(function_name, compile_func)
        return func
    return dec


@inclusion_tag(register, takes_context=True)
def object_comments(context, obj):
    ctype = obj.content_type
    template_name = [
        "%s/%s/inclusion_tags/object_comments.html" % (ctype.app_label, ctype.model),
        "%s/inclusion_tags/object_comments.html" % ctype.app_label,
        "jmbo/inclusion_tags/object_comments.html"
    ]
    can_comment, code = obj.can_comment(context['request'])
    context.update({
        'object': obj,
        'can_render_comment_form': can_comment,
        'can_comment_code': code
        })
    return template_name, context


@inclusion_tag(register, takes_context=True)
def object_header(context, obj):
    ctype = obj.content_type
    template_name = [
        "%s/%s/inclusion_tags/object_header.html" % (ctype.app_label, ctype.model),
        "%s/inclusion_tags/object_header.html" % ctype.app_label,
        "jmbo/inclusion_tags/object_header.html"
    ]
    context.update({'object': obj})
    return template_name, context


@inclusion_tag(register, takes_context=True)
def object_footer(context, obj):
    ctype = obj.content_type
    template_name = [
        "%s/%s/inclusion_tags/object_footer.html" % (ctype.app_label, ctype.model),
        "%s/inclusion_tags/object_footer.html" % ctype.app_label,
        "jmbo/inclusion_tags/object_footer.html"
    ]
    context.update({'object': obj})
    return template_name, context


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

        # Update context
        context.push()
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
            fallback_template_name = "jmbo/inclusion_tags/modelbase_%s.html" \
                    % type
            try:
                response = render_to_string(fallback_template_name, context)
            except TemplateDoesNotExist:
                if settings.TEMPLATE_DEBUG:
                    raise TemplateDoesNotExist({'resolved': template_name, \
                            'fallback': fallback_template_name})
                else:
                    response = ''
        finally:
            context.pop()

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
