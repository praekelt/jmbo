from django.conf.urls.defaults import url
from django.core.urlresolvers import reverse
from django.db.models.fields.related import RelatedField

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
        resource_name = 'content'
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
    
    def __init__(self, *args, **kwargs):
        self.as_leaf = kwargs.pop('as_leaf', False)
        self.get_type = ''
        self._content_type_fields = {}
        super(ModelBaseResource, self).__init__(*args, **kwargs)

    def get_list(self, request, **kwargs):
        if request:
            self.as_leaf = int(request.GET.get('as_leaf_class', 0))
        self.get_type = 'list'
        return super(ModelBaseResource, self).get_list(request, **kwargs)

    def get_detail(self, request, **kwargs):
        if request:
            self.as_leaf = int(request.GET.get('as_leaf_class', 0))
        self.get_type = 'detail'
        return super(ModelBaseResource, self).get_detail(request, **kwargs)

    def obj_get_list(self, request=None, **kwargs):
        qs = super(ModelBaseResource, self).obj_get_list(request, **kwargs)
        if self.as_leaf:
            leaf_qs = []
            self._content_type_fields = {}
            for obj in qs:
                leaf_qs.append(obj.as_leaf_class())
            return leaf_qs
        return qs
    
    def obj_get(self, request=None, **kwargs):
        obj = super(ModelBaseResource, self).obj_get(request, **kwargs)
        if self.as_leaf:
            return obj.as_leaf_class()
        return obj

    def dehydrate_image(self, bundle):
        if bundle.obj.image:
            if self.get_type == 'list':
                return bundle.obj.image_list_url
            elif self.get_type == 'detail':
                return bundle.obj.image_detail_url
        return None

    def dehydrate(self, bundle):
        bundle.data['content_type'] = bundle.obj.content_type.natural_key()
        if self.as_leaf:
            obj = bundle.obj
            if obj.content_type_id in self._content_type_fields:
                for f in self._content_type_fields[obj.content_type_id]:
                    bundle.data[f] = getattr(obj, f)
            else:
                extra_fields = []
                model = obj.content_type.model_class()
                for field in model._meta.fields:
                    name = field.name
                    if name not in self._meta.excludes and name not in bundle.data and not isinstance(field, RelatedField):
                        bundle.data[name] = getattr(obj, name)
                        extra_fields.append(name)
                self._content_type_fields[obj.content_type_id] = extra_fields
        return bundle
