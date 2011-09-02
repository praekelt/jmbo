from django.dispatch import receiver

from likes.signals import can_vote_test
from likes.exceptions import CannotVoteException

@receiver(can_vote_test)
def on_can_vote_test(sender, user, request, **kwargs):
    result, extra = sender.can_vote(request)
    if result:
        raise CannotVoteException(extra)
    return result, extra
