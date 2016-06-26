from django.conf.urls import include, url
from django.contrib import admin

from rest_framework import routers
from rest_framework_extras import discover

from jmbo.views import ObjectDetail, ObjectList
from jmbo import api as jmbo_api
from jmbo.tests import api as tests_api

admin.autodiscover()

router = routers.SimpleRouter()
router.register(
    r"jmbo-modelbase",
    jmbo_api.ModelBaseObjectsViewSet,
)
router.register(
    r"jmbo-modelbase-permitted",
    jmbo_api.ModelBasePermittedViewSet,
)
router.register(
    r"tests-testmodel",
    tests_api.TestModelObjectsViewSet,
)
router.register(
    r"tests-testmodel-permitted",
    tests_api.TestModelPermittedViewSet,
)

discover(router)

urlpatterns = [
    url(r"^admin/", include(admin.site.urls)),
    url(r'^api/(?P<version>(v1))/', include(router.urls)),
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
