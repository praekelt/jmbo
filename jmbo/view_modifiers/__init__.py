from django.utils.translation import ugettext as _

from jmbo.view_modifiers.items import CalEntryUpcomingItem, \
        CalEntryThisWeekendItem, CalEntryNext7DaysItem, \
        CalEntryThisMonthItem, IntegerFieldRangeItem, MostRecentItem, \
        MostLikedItem, TagItem, ThisMonthItem, ThisWeekItem


class ViewModifier(object):
    def __init__(self, request, ignore_defaults=False, *args, **kwargs):
        self.request = request
        self.ignore_defaults = ignore_defaults

        self.groups = {}
        for item in self.items:
            group = item.group
            if group:
                if group in self.groups:
                    self.groups[group].append(item)
                else:
                    self.groups[group] = [item, ]

        self.active_items = self.get_active_items()

    def get_active_items(self):
        active_items = []
        active_groups = []
        for item in self.items:
            if item.is_active(self.request):
                active_items.append(item)
                if item.group:
                    active_groups.append(item.group)

        # For each group without an active item fall back to defaults,
        # but only if defaults are not ignored(ignore_defaults=False).
        if not self.ignore_defaults:
            for item in self.items:
                if item.group:
                    if item.default and item.group not in active_groups:
                        active_items.append(item)
                        active_groups.append(item.group)

        # If we still don't have any active items fall back to defaults that
        # don't have groups, but only if defaults are not
        # ignored(ignore_defaults=False).
        if not active_items and not self.ignore_defaults:
            for item in self.items:
                if not item.group and item.default:
                    active_items.append(item)

        return active_items

    def modify(self, view):
        for item in self.active_items:
            view = item.modify(view)

        return view


class DateFieldIntervalViewModifier(ViewModifier):
    def __init__(self, request, field_name, base_url=None, *args, **kwargs):
        self.items = [
            CalEntryUpcomingItem(
                request=request,
                title=_("Upcoming"),
                get={'name': 'filter', 'value': 'recent'},
                field_name=field_name,
                base_url=base_url,
                default=True,
            ),
            CalEntryThisWeekendItem(
                request=request,
                title=_("This weekend"),
                get={'name': 'filter', 'value': 'weekend'},
                field_name=field_name,
                base_url=base_url,
            ),
            CalEntryNext7DaysItem(
                request=request,
                title=_("Next 7 days"),
                get={'name': 'filter', 'value': 'week'},
                field_name=field_name,
                base_url=base_url,
            ),
            CalEntryThisMonthItem(
                request=request,
                title=_("This month"),
                get={'name': 'filter', 'value': 'month'},
                field_name=field_name,
                base_url=base_url,
            ),
        ]
        super(DateFieldIntervalViewModifier, self).__init__(
            request,
            *args,
            **kwargs
        )


class DefaultViewModifier(ViewModifier):
    def __init__(self, request, base_url=None, *args, **kwargs):
        self.items = [
            MostRecentItem(
                request=request,
                title=_("Most recent"),
                get={'name': 'by', 'value': 'most-recent'},
                field_name='publish_on',
                base_url=base_url,
                default=True,
            ),
            MostLikedItem(
                request=request,
                title=_("Most liked"),
                get={'name': 'by', 'value': 'most-liked'},
                base_url=base_url,
                default=False,
            ),
            ThisWeekItem(
                request=request,
                title=_("This week"),
                get={'name': 'for', 'value': 'this-week'},
                field_name='publish_on',
                base_url=base_url,
                default=False,
            ),
            ThisMonthItem(
                request=request,
                title=_("This month"),
                get={'name': 'for', 'value': 'this-month'},
                field_name='publish_on',
                base_url=base_url,
                default=False,
            )
        ]
        super(DefaultViewModifier, self).__init__(request, *args, **kwargs)


class IntegerFieldRangeViewModifier(ViewModifier):
    def __init__(self, request, field_name, count, interval, *args, **kwargs):
        self.items = []

        ranges = range(0, count, interval)
        i = 0
        for range_start in ranges:
            range_end = range_start + interval
            range_start = range_start + 1
            self.items.append(IntegerFieldRangeItem(
                request=request,
                title="%s-%s" % (range_start, range_end),
                get={'name': 'range', 'value': range_start},
                field_name=field_name,
                filter_range=(range_start, range_end),
                default=i == 0,
            ))
            i += 1

        super(IntegerFieldRangeViewModifier, self).__init__(
            request,
            *args,
            **kwargs
        )


class CategoryTagViewModifier(ViewModifier):
    def __init__(self, request, category, *args, **kwargs):
        from category.models import Tag

        self.items = []
        tags = Tag.objects.filter(categories=category)

        for tag in tags:
            self.items.append(TagItem(
                request=request,
                title=tag.title,
                get={'name': 'tag', 'value': tag.slug},
                field_name='tag',
                tag=tag,
                default=False,
            ))

        super(CategoryTagViewModifier, self).__init__(request, *args, **kwargs)
