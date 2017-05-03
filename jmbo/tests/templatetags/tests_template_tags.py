from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def inject_foo(context):
    context["foo"] = "bar"
    return ""
