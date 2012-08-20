from django.dispatch import receiver
from likes.signals import likes_enabled_test, can_vote_test
from likes.exceptions import CannotVoteException, LikesNotEnabledException
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
