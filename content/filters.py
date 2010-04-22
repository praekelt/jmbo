from datetime import datetime, timedelta

from django.utils.translation import ugettext_lazy as _

from content.models import ModelBase

import django_filters

class DateRangeFilter(django_filters.DateRangeFilter):
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
            value = int(value)
            return self.options[value][1](qs, self.name)
        except (ValueError, TypeError):
            return qs.all()

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
    range = DateRangeFilter(
        name="created",
        label="Filter By",
    )
    class Meta:
        model = ModelBase
        fields = ['order', 'range']
