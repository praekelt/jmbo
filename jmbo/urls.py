from django.conf.urls import include, url

from jmbo.views import ObjectDetail, ObjectList, image_scale_url


urlpatterns = [
    url(
        r"^detail/(?P<slug>[\w-]+)/$",
        ObjectDetail.as_view(),
        name="modelbase-detail"
    ),
    url(
        r"^detail/(?P<category_slug>[\w-]+)/(?P<slug>[\w-]+)/$",
        ObjectDetail.as_view(),
        name="modelbase-categorized-detail"
    ),
    url(
        r"^list/(?P<app_label>[\w-]+)/(?P<model>[\w-]+)/$",
        ObjectList.as_view(),
        name="modelbase-list"
    ),
    url(
        r"^image-scale-url/(?P<pk>[\w-]+)/(?P<size>[\w-]+)/$",
        image_scale_url,
        name="image-scale-url"
    )
]
