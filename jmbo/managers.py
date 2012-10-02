from django.conf import settings
from django.db import models
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


class LocationAwareManager(GeoManager):
    def get_query_set(self):
        return LocationAwareQuerySet(self.model)
        
    
class PermittedManager(LocationAwareManager):
    def get_query_set(self):
        # Get base queryset and exclude based on state.
        queryset = super(PermittedManager, self).get_query_set().exclude(
            state='unpublished'
        )

        # Exclude objects in staging state if not in
        # staging mode (settings.STAGING = False).
        if not getattr(settings, 'STAGING', False):
            queryset = queryset.exclude(state='staging')

        # Filter objects for current site.
        queryset = queryset.filter(sites__id__exact=settings.SITE_ID)

        return queryset


class DefaultManager(LocationAwareManager):

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)
