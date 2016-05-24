from importlib import import_module

from django.conf.urls import patterns, include, url
from django.conf import settings

from jmbo.views import ObjectDetail, ObjectList


urlpatterns = patterns(
    "",
    (r"^jmbo/", include("jmbo.urls")),
    (r"^comments/", include("django_comments.urls")),

    url(
        r"^tests/detail/(?P<slug>[\w-]+)/$",
        ObjectDetail.as_view(),
        name="tests-branchmodel-detail"
    ),

    url(
        r"^tests/detail/(?P<slug>[\w-]+)/$",
        ObjectDetail.as_view(),
        name="tests-leafmodel-detail"
    ),

    url(
        r"^tests/detail/(?P<category_slug>[\w-]+)/(?P<slug>[\w-]+)/$",
        ObjectDetail.as_view(),
        name="tests-leafmodel-categorized-detail"
    ),

)
