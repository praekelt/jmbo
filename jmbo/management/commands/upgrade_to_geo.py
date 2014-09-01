import os

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.core import exceptions
from django.db import connection
from django.db.utils import DatabaseError
from south.models import MigrationHistory

import jmbo


class Command(BaseCommand):
    help = "Upgrade this Jmbo instance to use Jmbo's geo features."

    def handle(self, *args, **options):
        if jmbo.USE_GIS:
            call_command("migrate", "atlas")
            try:
                MigrationHistory.objects.get(app_name="jmbo", migration="0004_auto__add_field_modelbase_location")
                try:
                    # check that the migration added the location field
                    connection.cursor().execute("SELECT location_id FROM jmbo_modelbase;")
                except DatabaseError:
                    print("Running Jmbo GIS migration...")
                    from atlas.models import Location
                    from django.db import models
                    from south.db import db
                    db.add_column('jmbo_modelbase', 'location',
                        models.fields.related.ForeignKey(Location, null=True, blank=True),
                        keep_default=False)

            except MigrationHistory.DoesNotExist:
                #print("Jmbo GIS migration not run. Running it now...")
                call_command("migrate", "jmbo")

            print "Jmbo has been upgraded successfully."
        else:
            raise exceptions.ImproperlyConfigured("atlas and django.contrib.gis need to be added to your INSTALLED_APPS setting and your database engine must be set to one of the django.contrib.gis.db.backends.")
