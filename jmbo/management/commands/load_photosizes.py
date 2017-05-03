import os
from importlib import import_module

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core import serializers
from django.conf import settings

from photologue.models import PhotoSize


class Command(BaseCommand):
    help = "Scan apps for fixtures/photosizes.json and loads them."

    @transaction.atomic
    def handle(self, *args, **options):

        # Traverse over apps in reverse order. The reverse order is important
        # since the last app may override photosizes from other apps.
        for app in reversed(settings.INSTALLED_APPS):
            mod = import_module(app)
            fixtures = os.path.join(os.path.dirname(mod.__file__), 'fixtures', 'photosizes.json')

            if os.path.exists(fixtures):

                # Read json
                fp = open(fixtures, 'r')
                json = fp.read()
                fp.close()

                # Create / update objects
                for obj in serializers.deserialize('json', json):
                    # Blank pk
                    obj.object.id = None
                    try:
                        photosize = PhotoSize.objects.get(name=obj.object.name)
                    except PhotoSize.DoesNotExist:
                        # A new photosize
                        pass
                    else:
                        # Photosize already exists. It must be updated.
                        obj.object.id = photosize.id
                    obj.save()
