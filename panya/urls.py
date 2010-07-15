from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'panya.views',
    url(r'^peek/(?P<slug>[\w-]+)/$', 'object_peek', name='object_peek'),
    url(r'^(?P<category_slug>[\w-]+)/list/$', 'category_object_list', name='content_category_object_list'),
    url(r'^(?P<category_slug>[\w-]+)/(?P<slug>[\w-]+)/$', 'category_object_detail', name='content_category_object_detail'),
)
