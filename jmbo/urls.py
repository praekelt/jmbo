from django.conf.urls import patterns, include, url

from tastypie.api import Api

from jmbo.views import ObjectDetail, ObjectList
from jmbo.api import ModelBaseResource


v1_api = Api(api_name='v1')
v1_api.register(ModelBaseResource())


urlpatterns = patterns(
    '',

    url(
        r'^content/detail/(?P<slug>[\w-]+)/$',
        ObjectDetail.as_view(),
        name='object_detail'
    ),
    url(
        r'^content/list/(?P<app_label>[\w-]+)/(?P<model>[\w-]+)/$',
        ObjectList.as_view(),
        name='object_list'
    ),

    # Admin ajax urls
    (
        r'^admin/jmbo/publish-ajax/$',
        'jmbo.admin_views.publish_ajax',
        {},
        'jmbo-publish-ajax',
    ),

    (
        r'^admin/jmbo/unpublish-ajax/$',
        'jmbo.admin_views.unpublish_ajax',
        {},
        'jmbo-unpublish-ajax',
    ),

    (
        r'^admin/jmbo/edit-autosave-ajax/$',
        'jmbo.admin_views.edit_autosave_ajax',
        {},
        'jmbo-edit-autosave-ajax',
    ),

)
