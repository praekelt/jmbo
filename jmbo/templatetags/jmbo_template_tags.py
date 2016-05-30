from django import template
from django.utils.translation import ugettext as _
from django.template.base import VariableDoesNotExist


register = template.Library()


@register.tag
def get_related_items(parser, token):
    """Gets list of relations from object identified by a relation name.

    Syntax::

        {% get_related_items [relation_name] for [object] as [varname] [direction] %}
    """
    tokens = token.contents.split()
    if len(tokens) not in (6, 7):
        raise template.TemplateSyntaxError(
            "%r tag requires 6 arguments" % tokens[0]
        )

    if tokens[2] != 'for':
        raise template.TemplateSyntaxError(
            "Third argument in %r tag must be 'for'" % tokens[0]
        )

    if tokens[4] != 'as':
        raise template.TemplateSyntaxError(
            "Fifth argument in %r tag must be 'as'" % tokens[0]
        )

    direction = 'forward'
    if len(tokens) == 7:
        direction = tokens[6]

    return GetRelatedItemsNode(
        name=tokens[1], obj=tokens[3], as_var=tokens[5], direction=direction
    )


class GetRelatedItemsNode(template.Node):

    def __init__(self, name, obj, as_var, direction='forward'):
        self.name = template.Variable(name)
        self.obj = template.Variable(obj)
        self.as_var = template.Variable(as_var)
        self.direction = template.Variable(direction)

    def render(self, context):
        name = self.name.resolve(context)
        obj = self.obj.resolve(context)
        as_var = self.as_var.resolve(context)
        try:
            direction = self.direction.resolve(context)
        except template.VariableDoesNotExist:
            direction = 'forward'
        context[as_var] = obj.get_permitted_related_items(name, direction)
        return ''


@register.tag
def get_related_items_by_type(parser, token):
    """Gets list of relations from object identified by a content type.

    Syntax::

        {% get_related_items_by_type [content_type_app_label.content_type_model] for [object] as [varname] [direction] %}
    """
    tokens = token.contents.split()
    if len(tokens) not in (6, 7):
        raise template.TemplateSyntaxError(
            "%r tag requires 6 arguments" % tokens[0]
        )

    if tokens[2] != 'for':
        raise template.TemplateSyntaxError(
            "Third argument in %r tag must be 'for'" % tokens[0]
        )

    if tokens[4] != 'as':
        raise template.TemplateSyntaxError(
            "Fifth argument in %r tag must be 'as'" % tokens[0]
        )

    direction = 'forward'
    if len(tokens) == 7:
        direction = tokens[6]

    return GetRelatedItemsByTypeNode(
        name=tokens[1], obj=tokens[3], as_var=tokens[5], direction=direction
    )


class GetRelatedItemsByTypeNode(template.Node):

    def __init__(self, name, obj, as_var, direction='forward'):
        self.name = template.Variable(name)
        self.obj = template.Variable(obj)
        self.as_var = template.Variable(as_var)
        self.direction = template.Variable(direction)

    def render(self, context):
        name = self.name.resolve(context)
        content_type_app_label, content_type_model = name.split('.')
        obj = self.obj.resolve(context)
        as_var = self.as_var.resolve(context)
        try:
            direction = self.direction.resolve(context)
        except template.VariableDoesNotExist:
            direction = 'forward'
        context[as_var] = obj.get_permitted_related_items(
            direction=direction
        ).filter(
            content_type__app_label=content_type_app_label,
            content_type__model=content_type_model
        )
        return ''
