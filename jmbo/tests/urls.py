from django.conf.urls import patterns, include


urlpatterns = patterns(
    '',
    (r'^jmbo/', include('jmbo.urls')),
    (r'^comments/', include('django_comments.urls')),
)
