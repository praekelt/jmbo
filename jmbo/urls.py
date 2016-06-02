from django.conf.urls import include, url

#from tastypie.api import Api

from jmbo.views import ObjectDetail, ObjectList
#from jmbo.api import ModelBaseResource


#v1_api = Api(api_name="v1")
#v1_api.register(ModelBaseResource())


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
