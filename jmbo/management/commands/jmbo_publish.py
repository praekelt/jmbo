import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from jmbo.models import ModelBase


class Command(BaseCommand):
    help = "Publish or unpublish Jmbo objects."

    @transaction.atomic
    def handle(self, *args, **options):
        now = timezone.now()

        q1 = Q(publish_on__lte=now, retract_on__isnull=True)
        q2 = Q(publish_on__lte=now, retract_on__gt=now)
        ModelBase.objects.filter(state='unpublished').filter(q1 | q2).update(state='published')

        ModelBase.objects.filter(state='published').filter(retract_on__lte=now).update(state='unpublished')
