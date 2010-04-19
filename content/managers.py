from django.conf import settings
from django.db import models

class PermittedManager(models.Manager):
    def get_query_set(self):
        queryset = super(PermittedManager, self).get_query_set().exclude(state='unpublished')
        if getattr(settings, 'STAGING', False):
            queryset = queryset.exclude(state='staging')
        return queryset
