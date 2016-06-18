from django.conf.urls import include, url

from jmbo.views import ObjectDetail, ObjectList


urlpatterns = [
    url(
        r"^detail/(?P<slug>[\w-]+)/$",
        ObjectDetail.as_view(),
        name="jmbo-modelbase-detail"
    ),
    url(
        r"^detail/(?P<category_slug>[\w-]+)/(?P<slug>[\w-]+)/$",
        ObjectDetail.as_view(),
        name="jmbo-modelbase-categorized-detail"
    ),
    url(
        r"^list/(?P<app_label>[\w-]+)/(?P<model>[\w-]+)/$",
        ObjectList.as_view(),
        name="jmbo-modelbase-list"
    ),
]
