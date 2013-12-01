from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.comments.models import Comment

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
    if issubclass(sender, Comment):
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
