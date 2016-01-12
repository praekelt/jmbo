from django.conf.urls import url
from django.core.urlresolvers import NoReverseMatch

from tastypie.resources import ModelResource

from jmbo.models import ModelBase


class ModelBaseResource(ModelResource):

    class Meta:
        queryset = ModelBase.permitted.all()
        resource_name = 'modelbase'

    def get_resource_uri(self, bundle_or_obj=None, url_name='api_dispatch_list'):
        """The resource_uri must point to the leaf class if possible"""
        if bundle_or_obj is not None:
            try:
                leaf = bundle_or_obj.obj.as_leaf_class()
            except AttributeError:
                pass
            else:
                # Prevent circular import
                from jmbo.urls import v1_api
                # Registry convention
                resource = v1_api._registry.get(leaf.__class__.__name__.lower())
                if resource:
                   return resource.get_resource_uri(leaf, url_name)

        return super(ModelBaseResource, self).get_resource_uri(bundle_or_obj, url_name)

    def dehydrate(self, bundle):
        bundle.data['permalink'] = bundle.obj.get_absolute_url()
        bundle.data['image_detail_url'] = ''
        if bundle.obj.image:
            try:
                bundle.data['image_detail_url'] = bundle.obj.image_detail_url
            except AttributeError:
                pass
        return bundle
