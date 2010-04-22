from django import template

register = template.Library()

@register.tag
def smart_query_string(parser, token):
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
