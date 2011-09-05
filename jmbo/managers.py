from django.conf import settings
from django.db import models


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
        return queryset
