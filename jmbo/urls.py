from django.conf.urls.defaults import patterns, url, include

from tastypie.api import Api

from jmbo.api import ModelBaseResource


v1_api = Api(api_name='v1')
v1_api.register(ModelBaseResource())


urlpatterns = patterns(
    '',

    url(
        r'^content/detail/(?P<slug>[\w-]+)/$',
        'jmbo.views.object_detail',
        {},
        name='object_detail'
    ),
    url(
        r'^content/list/(?P<app_label>[\w-]+)/(?P<model>[\w-]+)/$',
        'jmbo.views.object_list',
        {},
        name='object_list'
    ),
    url(
        r'^content/peek/(?P<slug>[\w-]+)/$',
        'jmbo.views.object_peek',
        {},
        name='object_peek'
    ),
    url(
        r'^content/(?P<category_slug>[\w-]+)/list/$',
        'jmbo.views.category_object_list',
        {},
        name='category_object_list'
    ),
    url(
        r'^content/(?P<category_slug>[\w-]+)/(?P<slug>[\w-]+)/$',
        'jmbo.views.category_object_detail',
        {},
        name='category_object_detail'
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

)
