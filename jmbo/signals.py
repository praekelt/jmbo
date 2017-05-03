from django.db.models.signals import post_save, m2m_changed
from django.db import IntegrityError
from django.dispatch import receiver

import django_comments
from likes.signals import likes_enabled_test, can_vote_test
from likes.exceptions import CannotVoteException, LikesNotEnabledException
from secretballot.models import Vote

import jmbo


@receiver(likes_enabled_test)
def on_likes_enabled_test(sender, instance, request, **kwargs):
    if issubclass(sender, jmbo.models.ModelBase):
        if not instance.likes_enabled:
            raise LikesNotEnabledException()
        return True


@receiver(can_vote_test)
def on_can_vote_test(sender, instance, user, request, **kwargs):
    if issubclass(sender, jmbo.models.ModelBase):
        result, extra = instance.can_vote(request)
        if not result:
            raise CannotVoteException(extra)
        return result, extra


@receiver(post_save)
def on_comment_post_save(sender, **kwargs):
    model = django_comments.get_model()
    if issubclass(sender, model):
        obj = kwargs['instance'].content_object
        if isinstance(obj, jmbo.models.ModelBase):
            obj.comment_count = obj._comment_count
            obj.save(set_modified=False)


@receiver(post_save, sender=Vote)
def on_vote_post_save(sender, **kwargs):
    obj = kwargs['instance'].content_object
    if isinstance(obj, jmbo.models.ModelBase):
        obj.vote_total = obj._vote_total
        obj.save(set_modified=False)


@receiver(m2m_changed)
def check_slug(sender, instance, **kwargs):
    """Slug must be unique per site"""
    if isinstance(instance, jmbo.models.ModelBase) \
            and (kwargs['action'] == 'post_add') \
            and sender.__name__.endswith('_sites'):
        for site in instance.sites.all():
            q = jmbo.models.ModelBase.objects.filter(
                    slug=instance.slug, sites=site).exclude(id=instance.id)
            if q.exists():
                raise IntegrityError(
                    "The slug %s is already in use for site %s by %s" %
                    (instance.slug, site.domain, q[0].title))
