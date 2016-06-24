import json

from rest_framework import viewsets
from rest_framework.serializers import HyperlinkedModelSerializer, \
    ReadOnlyField, Serializer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.reverse import reverse
from rest_framework_extras.serializers import FormMixin

from jmbo.models import ModelBase
from jmbo.admin import ModelBaseAdmin


class PropertiesMixin(Serializer):
    image_detail_url = ReadOnlyField()

    class Meta:
        fields = ("image_detail_url",)


class HyperlinkedModelBaseSerializer(
    FormMixin, PropertiesMixin, HyperlinkedModelSerializer
    ):

    class Meta:
        model = ModelBase
        admin = ModelBaseAdmin


class CommonRoutes(object):

    @detail_route(methods=["get"])
    def images(self, request, pk, **kwargs):
        li = []
        for mbi in self.get_object().modelbaseimage_set.all():
            # I can't get reverse('jmbo-image-detail', args=(mbi.image.pk,),
            # request=self.request) to work, so use a workaround.
            # xxx: DRF does not prefix base_name with app_label. Investigate.
            reversed = "%s%s/" % (reverse("image-list", request=self.request), mbi.image.pk)
            li.append(reversed)
        return Response({"status": "success", "images": li})


class ModelBaseObjectsViewSet(CommonRoutes, viewsets.ModelViewSet):
    queryset = ModelBase.objects.all()
    serializer_class = HyperlinkedModelBaseSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (DjangoModelPermissions,)

    @detail_route(methods=["post"])
    def publish(self, request, pk, **kwargs):
        self.get_object().publish()
        return Response({"status": "success"})

    @detail_route(methods=["post"])
    def unpublish(self, request, pk, **kwargs):
        self.get_object().unpublish()
        return Response({"status": "success"})


class ModelBasePermittedViewSet(CommonRoutes, viewsets.ModelViewSet):
    queryset = ModelBase.permitted.all()
    serializer_class = HyperlinkedModelBaseSerializer
