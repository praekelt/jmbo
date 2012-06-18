from tastypie.resources import ModelResource

from jmbo.models import ModelBase


class ModelBaseResource(ModelResource):

    class Meta:
        queryset = ModelBase.permitted.all()
        resource_name = 'modelbase'

    def dehydrate(self, bundle):
        bundle.data['resource_name'] = self._meta.resource_name
        bundle.data['permalink'] = bundle.obj.get_absolute_url()
        return bundle
