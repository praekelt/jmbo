from django.db.models import Q
from django.utils import timezone

from celery import task
from celery.task.schedules import crontab
from celery.decorators import periodic_task

from jmbo.models import ModelBase


@periodic_task(run_every=crontab(hour='*', minute='*/10', day_of_week='*'), ignore_result=True)
def publish_scheduled_content():
    now = timezone.now()
    q1 = Q(publish_on__lte=now, retract_on__isnull=True)
    q2 = Q(publish_on__lte=now, retract_on__gt=now)
    ModelBase.objects.filter(state='unpublished').filter(q1 | q2).update(state='published')
    ModelBase.objects.filter(state='published').filter(retract_on__lte=now).update(state='unpublished')
