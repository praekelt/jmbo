from django.db import models
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings

from crum import get_current_request

from jmbo import USE_GIS


class BaseManager(models.Manager):
    pass


if USE_GIS:
    from django.contrib.gis.db.models import GeoManager
    from django.contrib.gis.db.models.query import GeoQuerySet

    DB_ENGINE = settings.DATABASES['default']['ENGINE']

    class LocationAwareQuerySet(GeoQuerySet):

        # annotates each object with a distance attribute
        def distance(self, point):
            # Join location attributes
            qs = self.select_related("location").exclude(location__coordinates__isnull=True)

            # Calculate spherical distance and store in distance attribute
            if DB_ENGINE.rfind('postgis') >= 0:
                sql = 'ST_Distance("atlas_location"."coordinates", ST_GeomFromText(\'%s\', %d))' \
                        % (str(point), point.srid)
            elif DB_ENGINE.rfind('mysql') >= 0:
                sql = 'distance_sphere(`atlas_location`.`coordinates`, geomfromtext(\'%s\', %d))' \
                        % (str(point), point.srid)
            elif DB_ENGINE.rfind('spatialite') >= 0:
                sql = 'ST_Distance("atlas_location"."coordinates", ST_GeomFromText(\'%s\', %d))' \
                        % (str(point), point.srid)
            else:
                raise ValueError("Distance calculations are not supported for ModelBase using this database.")

            return qs.extra(select={'distance': sql})

    BaseManager.get_query_set = lambda manager: LocationAwareQuerySet(manager.model)


class PermittedManager(BaseManager):

    def get_queryset(self, for_user=None):
        #import pdb;pdb.set_trace()
        is_staff = getattr(for_user, 'is_staff', False)
        queryset = super(PermittedManager, self).get_queryset()

        # Exclude unpublished if user is not staff
        if not is_staff:
            queryset = queryset.exclude(
                state='unpublished'
            )

        # Filter objects for current site
        site = get_current_site(get_current_request())
        queryset = queryset.filter(sites__id__exact=site.id)

        return queryset


class DefaultManager(BaseManager):

    # todo: mix in sites here. Needs computed field to work.
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)
