from django.conf.urls.defaults import url
from django.core.urlresolvers import reverse

from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS

from jmbo.models import ModelBase


class ModelBaseResource(ModelResource):

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
        include_absolute_url = True
        # these fields are used internally and should not be exposed
        excludes = ('id', 'view_count', 'date_taken', 'crop_from', 'effect',
        'state', 'publish_on', 'retract_on', 'class_name')

    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<slug>[\w-]+)/$" % self._meta.resource_name,
                self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]
    
    def get_resource_uri(self, bundle_or_obj):
        obj = bundle_or_obj if isinstance(bundle_or_obj, ModelBase) else bundle_or_obj.obj
        return reverse("api_dispatch_detail", kwargs={'api_name': self._meta.api_name,
            'resource_name': self._meta.resource_name, 'slug': obj.slug})

    def dehydrate_image(self, bundle):
        if bundle.obj.image:
            return {'image_list_uri': bundle.obj.image_list_url,
                'image_detail_uri': bundle.obj.image_detail_url}
        return None

    def dehydrate(self, bundle):
        bundle.data['content_type'] = bundle.obj.content_type.natural_key()
        return bundle
