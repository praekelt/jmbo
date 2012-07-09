import datetime

from django.conf import settings
from django.db import models
from django.db.models import Q


class PermittedManager(models.Manager):
    def get_query_set(self):
        # Get base queryset and exclude based on state.
        queryset = super(PermittedManager, self).get_query_set().exclude(
            state='unpublished'
        )

        # Exclude objects in staging state if not in
        # staging mode (settings.STAGING = False).
        if not getattr(settings, 'STAGING', False):
            queryset = queryset.exclude(state='staging')

        # Filter objects for current site.
        queryset = queryset.filter(sites__id__exact=settings.SITE_ID)

        # Filter published date
        now = datetime.datetime.now()
        q1 = Q(publish_on__isnull=True, retract_on__isnull=True)
        q2 = Q(publish_on__lte=now, retract_on__isnull=True)
        q3 = Q(publish_on__isnull=True, retract_on__gt=now)
        q4 = Q(publish_on__lte=now, retract_on__gt=now)
        queryset = queryset.filter(q1|q2|q3|q4)

        return queryset


class DefaultManager(models.Manager):
    
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)

