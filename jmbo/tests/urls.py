from django.conf.urls import include, url
from django.contrib import admin

from rest_framework import routers
from rest_framework_extras import discover

from jmbo.views import ObjectDetail, ObjectList
from jmbo.api import base
from jmbo.tests.api import base as tests_base

admin.autodiscover()

router = routers.SimpleRouter()
router.register(r"jmbo-modelbases", base.ModelBaseObjectsViewSet)
router.register(r"jmbo-permitted-modelbases", base.ModelBasePermittedViewSet)
router.register(r"tests-testmodels", tests_base.TestModelObjectsViewSet)
router.register(r"tests-permitted-testmodels", tests_base.TestModelPermittedViewSet)

discover(router)

urlpatterns = [
    url(r"^admin/", include(admin.site.urls)),
    url(r'^api/v1/', include(router.urls)),
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
