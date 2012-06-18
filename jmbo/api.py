from django.conf.urls.defaults import url

from tastypie.resources import ModelResource

from jmbo.models import ModelBase


class ModelBaseResource(ModelResource):

    class Meta:
        queryset = ModelBase.permitted.all()
        resource_name = 'modelbase'

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<slug>[\w-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

    def dehydrate(self, bundle):
        bundle.data['resource_name'] = self._meta.resource_name
        bundle.data['permalink'] = bundle.obj.get_absolute_url()
        return bundle
