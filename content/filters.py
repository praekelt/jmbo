from datetime import datetime, timedelta

from django.utils.translation import ugettext_lazy as _

from content.models import ModelBase

import django_filters

class IntervalFilter(django_filters.DateRangeFilter):
    """
    Filters based on week (in reality the last 7 days) and month.
    """
    options = {
        'week': (_('This Week'), lambda qs, name: qs.filter(**{
            '%s__gte' % name: (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d'),
            '%s__lt' % name: (datetime.today()+timedelta(days=1)).strftime('%Y-%m-%d'),
        })),
        'month': (_('This Month'), lambda qs, name: qs.filter(**{
            '%s__year' % name: datetime.today().year,
            '%s__month' % name: datetime.today().month
        })),
    }
    def filter(self, qs, value):
        try:
            return self.options[value][1](qs, self.name)
        except KeyError:
            return qs

class OrderFilter(ChoiceFilter):
    pass

def order_action(qs, value):
    if value == '' or 'most-recent':
        return qs.order_by('-created')

class ContentFilter(django_filters.FilterSet):
    order_choices = ('most-recent', 'most-liked')
    order = django_filters.ChoiceFilter(
        name='classname', 
        label='Order By',
        action=order_action,
        choices=(
            ('most-recent', 'Most Recent'),
            ('most-liked', 'Most Liked'),
        )
    )
    interval = IntervalFilter(
        name="created",
        label="Filter By",
    )
    class Meta:
        model = ModelBase
        fields = ['order', 'interval']
