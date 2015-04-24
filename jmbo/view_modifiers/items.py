from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import RegexURLResolver, Resolver404
from django.utils.encoding import smart_str

from secretballot.models import Vote


# Base Item Class
class Item(object):
    def __init__(self, request, title, default, group=None, *args, **kwargs):
        self.request = request
        self.title = title
        self.default = default
        self.group = group


class GetItem(Item):
    def __init__(self, request, title, get, field_name='', base_url=None, \
            default=False, *args, **kwargs):
        get['value'] = str(get['value'])
        self.get = get
        self.field_name = field_name
        self.base_url = base_url
        super(GetItem, self).__init__(request, title, default, *args, **kwargs)

    def is_active(self, request):
        if hasattr(self, 'get'):
            if self.get['name'] in request.GET:
                # Strip away potential #abcd suffix from value
                value = self.get['value']
                value = value.split('#')[0]
                return request.GET[self.get['name']] == value

        return False

    def modify(self, view):
        """
        adds the get item as extra context
        """
        view.params['extra_context'][self.get['name']] = self.get['value']
        return view

    def get_absolute_url(self):
        addition_pairs = [(self.get['name'], self.get['value']), ]
        remove_keys = ['page', ]
        q = dict([(k, v) for k, v in self.request.GET.items()])
        for key in remove_keys:
            if key in q:
                del q[key]
        for key, value in addition_pairs:
            if key:
                if value:
                    q[key] = value
                else:
                    q.pop(key, None)
            qs = '&'.join(['%s=%s' % (k, v) for k, v in q.items()])

        get_string = '?' + qs if len(q) else ''
        if self.base_url:
            return "%s%s" % (self.base_url, get_string)
        else:
            return get_string


class URLPatternItem(Item):
    def __init__(self, request, title, path, matching_pattern_names, default):
        self.path = path
        self.matching_pattern_names = matching_pattern_names
        super(URLPatternItem, self).__init__(request, title, default)

    def resolve_pattern_name(self, resolver, path):
        tried = []
        match = resolver.regex.search(path)
        if match:
            new_path = path[match.end():]
            for pattern in resolver.url_patterns:
                try:
                    sub_match = pattern.resolve(new_path)
                except Resolver404, e:
                    sub_tried = e.args[0].get('tried')
                    if sub_tried is not None:
                        tried.extend([(pattern.regex.pattern + \
                                '   ' + t) for t in sub_tried])
                    else:
                        tried.append(pattern.regex.pattern)
                else:
                    if sub_match:
                        sub_match_dict = dict([(smart_str(k), v) for \
                                k, v in match.groupdict().items()])
                        sub_match_dict.update(resolver.default_kwargs)
                        for k, v in sub_match[2].iteritems():
                            sub_match_dict[smart_str(k)] = v
                        try:
                            return pattern.name
                        except AttributeError:
                            return self.resolve_pattern_name(pattern, new_path)
                    tried.append(pattern.regex.pattern)
            raise Resolver404({'tried': tried, 'path': new_path})
        raise Resolver404({'path': path})

    def is_active(self, request):
        urlconf = getattr(request, "urlconf", settings.ROOT_URLCONF)
        resolver = RegexURLResolver(r'^/', urlconf)

        url_name = self.resolve_pattern_name(resolver, request.path)
        return url_name in self.matching_pattern_names

    def modify(self, view):
        return view

    def get_absolute_url(self):
        return self.path


# Specific Items
class CalEntryUpcomingItem(GetItem):
    def modify(self, view):
        view.params['queryset'] = view.params['queryset'].upcoming()
        return view


class CalEntryNext7DaysItem(GetItem):
    def modify(self, view):
        view.params['queryset'] = view.params['queryset'].next7days()
        return view


class CalEntryThisWeekendItem(GetItem):
    def modify(self, view):
        view.params['queryset'] = view.params['queryset'].thisweekend()
        return view


class CalEntryThisMonthItem(GetItem):
    def modify(self, view):
        view.params['queryset'] = view.params['queryset'].thismonth()
        return view


class IntegerFieldRangeItem(GetItem):
    def __init__(self, request, title, get, field_name, filter_range, \
            default=False):
        self.filter_range = filter_range
        super(IntegerFieldRangeItem, self).__init__(
            request=request,
            title=title,
            get=get,
            field_name=field_name,
            default=default
        )

    def modify(self, view):
        view.params['queryset'] = view.params['queryset'].filter(
            **{"%s__range" % self.field_name: self.filter_range}
        )
        return view


class MostRecentItem(GetItem):
    def modify(self, view):
        view.params['queryset'] = view.params['queryset'].order_by(
            '-%s' % self.field_name
        )
        return view


class MostLikedItem(GetItem):
    def modify(self, view):
        queryset = view.params['queryset']
        view.params['queryset'] = queryset.order_by('-vote_total')
        return view


class PagingCountItem(GetItem):
    def modify(self, view):
        try:
            view.params['paginate_by'] = int(self.get['value'])
        except ValueError:
            pass
        return view


class ThisMonthItem(GetItem):
    def modify(self, view):
        view.params['queryset'] = view.params['queryset'].filter(**{
            '%s__year' % self.field_name: datetime.today().year,
            '%s__month' % self.field_name: datetime.today().month
        })
        return view


class ThisWeekItem(GetItem):
    def modify(self, view):
        view.params['queryset'] = view.params['queryset'].filter(**{
            '%s__gte' % self.field_name: (datetime.today() - \
                    timedelta(days=7)).strftime('%Y-%m-%d'),
            '%s__lt' % self.field_name: (datetime.today() + \
                    timedelta(days=1)).strftime('%Y-%m-%d'),
        })
        return view


class TagItem(GetItem):
    def __init__(self, request, title, get, field_name, tag, default=False):
        self.tag = tag
        super(TagItem, self).__init__(
            request=request,
            title=title,
            get=get,
            field_name=field_name,
            default=default
        )

    def modify(self, view):
        view.params['queryset'] = view.params['queryset'].filter(tags=self.tag)
        return view
