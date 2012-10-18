from django.conf.urls.defaults import url
from django.core.urlresolvers import reverse

from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.bundle import Bundle

from jmbo.models import ModelBase


class SlugResource(ModelResource):
    
    class Meta:
        include_absolute_url = True
        abstract = True
    
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<slug>[\w-]+)/$" % self._meta.resource_name,
                self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]
    
    def get_resource_uri(self, bundle_or_obj, url_name='api_dispatch_list'):
        url_kwargs = {'api_name': self._meta.api_name, 'resource_name': self._meta.resource_name}
        if bundle_or_obj:
            url_kwargs['slug'] = bundle_or_obj.obj.slug if isinstance(bundle_or_obj, Bundle) else bundle_or_obj.slug
        return reverse(url_name, kwargs=url_kwargs)


class ModelBaseResource(SlugResource):

    class Meta:
        queryset = ModelBase.permitted.all()
        resource_name = 'modelbase'
        # NB. implement filtering properly later
        '''filtering = {
            'categories': ALL_WITH_RELATIONS,
            'primary_category': ALL_WITH_RELATIONS,
            'content_type': ALL_WITH_RELATIONS,
        }'''
        max_limit = 20
        # these fields are used internally and should not be exposed
        excludes = ('id', 'view_count', 'date_taken', 'crop_from', 'effect',
        'state', 'publish_on', 'retract_on', 'class_name')


    def dehydrate_image(self, bundle):
        if bundle.obj.image:
            return {'image_list_uri': bundle.obj.image_list_url,
                'image_detail_uri': bundle.obj.image_detail_url}
        return None


    def dehydrate(self, bundle):
        bundle.data['content_type'] = bundle.obj.content_type.natural_key()
        return bundle
