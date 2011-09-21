from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'jmbo.views',
    url(r'^content/peek/(?P<slug>[\w-]+)/$', 'object_peek', \
            name='object_peek'),
    url(r'^content/(?P<category_slug>[\w-]+)/list/$', 'category_object_list', \
            name='content_category_object_list'),
    url(r'^content/(?P<category_slug>[\w-]+)/(?P<slug>[\w-]+)/$', \
            'category_object_detail', name='content_category_object_detail'),
)
