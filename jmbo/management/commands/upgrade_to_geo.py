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
            call_command("migrate", *["atlas"])
            try:
                MigrationHistory.objects.get(app_name="jmbo", migration="0004_auto__add_field_modelbase_location")
                try:
                    # check that the migration added the location field
                    connection.cursor().execute("SELECT location_id FROM jmbo_modelbase;")
                except DatabaseError:
                    # create a migration and run it
                    call_command("schemamigration", *["jmbo"], **{"--add-field": "modelbase.location"})
                    call_command("migrate", *["jmbo"])

                    # pretend it didn't happen
                    qs = MigrationHistory.objects.filter(app_name="jmbo").order_by("-applied")[0:1]
                    migration = qs[0]
                    # delete the migration history entry
                    qs.delete()
                    # delete the migration file
                    migration_path = os.path.join(os.path.dirname(jmbo.__file__), "migrations/%s.py" % migration.migration)
                    os.remove(migration_path)

            except MigrationHistory.DoesNotExist:
                call_command("migrate", *["jmbo"])

            print "Jmbo has been upgraded successfully."
        else:
            raise exceptions.ImproperlyConfigured("atlas and django.contrib.gis need to be added to your INSTALLED_APPS setting.")
