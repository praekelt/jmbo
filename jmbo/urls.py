from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'jmbo.views',
    url(
        r'^content/detail/(?P<slug>[\w-]+)/$',
        'object_detail',
        {},
        name='object_detail'
    ),
    url(
        r'^content/list/(?P<app_label>[\w-]+)/(?P<model>[\w-]+)/$',
        'object_list',
        {},
        name='object_list'
    ),
    url(
        r'^content/peek/(?P<slug>[\w-]+)/$',
        'object_peek',
        {},
        name='object_peek'
    ),
    url(
        r'^content/(?P<category_slug>[\w-]+)/list/$',
        'category_object_list',
        {},
        name='category_object_list'
    ),
    url(
        r'^content/(?P<category_slug>[\w-]+)/(?P<slug>[\w-]+)/$',
        'category_object_detail',
        {},
        name='category_object_detail'
    ),
)
