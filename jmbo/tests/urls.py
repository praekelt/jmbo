from django.conf.urls import include, url
from django.contrib import admin

from rest_framework import routers
from rest_framework_extras import discover

from jmbo.views import ObjectDetail, ObjectList
from jmbo.api import base
from jmbo.tests.api import base as tests_base

admin.autodiscover()

router = routers.SimpleRouter()
router.register(
    r"jmbo-modelbase",
    base.ModelBaseObjectsViewSet,
    #"jmbo-modelbase"
)
router.register(
    r"jmbo-permitted-modelbase",
    base.ModelBasePermittedViewSet,
    #"jmbo-permitted-modelbase"
)
router.register(
    r"tests-testmodel",
    tests_base.TestModelObjectsViewSet,
    #"tests-testmodel"
)
router.register(
    r"tests-permitted-testmodel",
    tests_base.TestModelPermittedViewSet,
    #"tests-permitted-testmodel"
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
