from django.apps import AppConfig
from django.db.models.signals import post_migrate

import secretballot


def do_enable_voting_on(sender, **kwargs):
    from jmbo import models
    secretballot.enable_voting_on(
        models.ModelBase,
        manager_name="secretballot_objects",
        total_name="secretballot_added_vote_total"
    )


class JmboAppConfig(AppConfig):
    name = "jmbo"

    def ready(self):
        post_migrate.connect(do_enable_voting_on)
