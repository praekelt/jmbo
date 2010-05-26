from datetime import datetime

from django import template

register = template.Library()

@register.simple_tag
def smart_url(url_callable, obj):
    return url_callable(obj)

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
            qs = '&'.join(['%s=%s' % (k, v) for k, v in q.items()])
        return '?' + qs if len(q) else ''

@register.tag
def humanize_time_diff(parser, token):
    try:
        tag_name, date_obj, suffix = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%s requires exactly two argument" % tag_name
    
    return HumanizeTimeDifference(date_obj, suffix)

class HumanizeTimeDifference(template.Node):
    """
    Adapted from Django Snippet 412
    
    Returns a humanized string representing time difference
    between now() and the input timestamp.
    
    The output rounds up to days, hours, minutes, or seconds.
    4 days 5 hours returns '4 days'
    0 days 4 hours 3 minutes returns '4 hours', etc...
    """
    def __init__(self, date_obj, suffix):
        self.date_obj = template.Variable(date_obj)
        self.suffix = template.Variable(suffix)

    def render(self, context):
        date_obj = self.date_obj.resolve(context)
        suffix = self.suffix.resolve(context)
        
        if date_obj:
            time_difference = datetime.now() - date_obj
            days = time_difference.days
            hours = time_difference.seconds / 3600
            minutes = time_difference.seconds % 3600 / 60
            seconds = time_difference.seconds % 3600 % 60
           
            if days > 0:
                if days == 1: return "Yesterday"
                else: dt_str = "Days"
                return "%s %s %s" % (days, dt_str, suffix)
            elif hours > 0:
                if hours == 1: dt_str = "Hour"
                else: dt_str = "Hours"
                return "%s %s %s" % (hours, dt_str, suffix)
            elif minutes > 0:
                if minutes == 1: dt_str = "Minute"
                else: dt_str = "Minutes"
                return "%s %s %s" % (minutes, dt_str, suffix)
            elif seconds > 0:
                if seconds == 1: dt_str = "Second"
                else: dt_str = "Seconds"
                return "%s %s %s" % (seconds, dt_str, suffix)
            elif seconds == 0:
                return "Just Now"
        return ""
