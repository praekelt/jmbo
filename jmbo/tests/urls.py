from django.conf.urls import include, url
from django.contrib import admin

from jmbo.views import ObjectDetail, ObjectList


admin.autodiscover()

urlpatterns = [
    url(r"^admin/", include(admin.site.urls)),
    url(r"^jmbo/", include("jmbo.urls")),
    url(r"^comments/", include("django_comments.urls")),
    url(r"^likes/", include("likes.urls")),

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
]
