from django.conf.urls.defaults import url
from django.core.urlresolvers import reverse
from django.db.models.fields.related import RelatedField
from django.contrib.contenttypes.models import ContentType

from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.bundle import Bundle
from tastypie.authorization import Authorization
from tastypie.exceptions import BadRequest

from jmbo.models import ModelBase


class SlugResource(ModelResource):
    
    class Meta:
        abstract = True
    
    def override_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<slug>[\w-]+)/$" % self._meta.resource_name,
                self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]
    
    def get_resource_uri(self, bundle_or_obj, url_name='api_dispatch_detail'):
        url_kwargs = {'api_name': self._meta.api_name, 'resource_name': self._meta.resource_name}
        if bundle_or_obj:
            url_kwargs['slug'] = bundle_or_obj.obj.slug if isinstance(bundle_or_obj, Bundle) else bundle_or_obj.slug
        return reverse(url_name, kwargs=url_kwargs)


class ModelBaseResource(SlugResource):

    class Meta:
        queryset = ModelBase.permitted.all()
        include_absolute_url = True
        resource_name = 'content'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get', 'put']
        max_limit = 20
        # these fields are used internally and should not be exposed
        excludes = ('id', 'view_count', 'date_taken', 'crop_from', 'effect',
        'state', 'publish_on', 'retract_on', 'class_name')
        authorization = Authorization()
    
    def __init__(self, *args, **kwargs):
        self.as_leaf = kwargs.pop('as_leaf', False)
        self.get_type = ''
        self._content_type_fields = {}
        super(ModelBaseResource, self).__init__(*args, **kwargs)
    
    def build_filters(self, filters=None):
        if 'content_type' in filters:
            app, model = filters.pop('content_type')[0].split(',')
            model = ContentType.objects.get(app_label=app, model=model).model_class()
            self._meta.object_class = model
            self._meta.queryset = model.permitted.all()
            self.fields.update(ModelBaseResource.get_fields([], self._meta.excludes))
        return super(ModelBaseResource, self).build_filters(filters)
    
    def obj_update(self, bundle, request, **kwargs):
        if len(bundle.data) == 1 and 'like' in bundle.data:
            from likes.views import like
            obj = ModelBase.permitted.get(slug=kwargs['slug'])
            can_vote, reason = obj.can_vote(request)
            if can_vote:
                like(bundle.request, "%s-%s" % (obj.content_type.app_label, obj.content_type.model), obj.id, 1)
                return bundle
            raise BadRequest("User cannot like this object: %s" % reason) 
        else:
            raise BadRequest("Invalid PUT data")

    def get_list(self, request, **kwargs):
        if request:
            self.as_leaf = int(request.GET.get('as_leaf_class', 0)) \
                if 'content_type' not in request.GET else False
        self.get_type = 'list'
        return super(ModelBaseResource, self).get_list(request, **kwargs)

    def get_detail(self, request, **kwargs):
        if request:
            self.as_leaf = int(request.GET.get('as_leaf_class', 0)) \
                if 'content_type' not in request.GET else False
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
        bundle.data['can_vote'] = bundle.obj.can_vote(bundle.request)[0]
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
