from django.dispatch import receiver

from likes.signals import likes_enabled_test, can_vote_test
from likes.exceptions import CannotVoteException, LikesNotEnabledException


@receiver(likes_enabled_test)
def on_likes_enabled_test(sender, request, **kwargs):
    if not sender.likes_enabled:
        raise LikesNotEnabledException()
    return True


@receiver(can_vote_test)
def on_can_vote_test(sender, user, request, **kwargs):
    result, extra = sender.can_vote(request)
    if not result:
        raise CannotVoteException(extra)
    return result, extra
