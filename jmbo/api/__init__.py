import logging
import json

from django.conf import settings

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


logger = logging.getLogger("django")

if settings.REST_FRAMEWORK.get("DEFAULT_VERSIONING_CLASS") != \
    "rest_framework.versioning.URLPathVersioning":
    logger.warning("""Jmbo: URLPathVersioning is not set as \
DEFAULT_VERSIONING_CLASS. It is strongly recommended to update your \
settings.""")


class PropertiesMixin(Serializer):
    image_detail_url = ReadOnlyField()

    class Meta:
        fields = ("image_detail_url",)


class ModelBaseSerializer(
    FormMixin, PropertiesMixin, HyperlinkedModelSerializer
    ):

    class Meta:
        model = ModelBase
        admin = ModelBaseAdmin

    def get_extra_kwargs(self):
        # We specify a base_name at router registration and this is a way to
        # sneak in view_name so it resolves properly.
        di = super(ModelBaseSerializer, self).get_extra_kwargs()
        meta = self.Meta.model._meta
        prefix = ("%s-%s" % (meta.app_label, meta.object_name)).lower()
        if isinstance(self.context["view"], ModelBasePermittedViewSet):
            di["url"] = {"view_name": "%s-permitted-detail" % prefix}
        else:
            di["url"] = {"view_name": "%s-detail" % prefix}
        return di


class CommonRoutes(object):

    @detail_route(methods=["get"])
    def images(self, request, pk, **kwargs):
        li = []
        for image in self.get_object().images.all():
            # I can't get reverse('jmbo-image-detail', args=(image.pk,),
            # request=self.request) to work, so use a workaround.
            # xxx: DRF does not prefix base_name with app_label. Investigate.
            reversed = "%s%s/" % (reverse("image-list", request=self.request), image.pk)
            li.append(reversed)
        return Response(li)


class ModelBaseObjectsViewSet(CommonRoutes, viewsets.ModelViewSet):
    queryset = ModelBase.objects.all()
    serializer_class = ModelBaseSerializer
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


class ModelBasePermittedViewSet(CommonRoutes, viewsets.ReadOnlyModelViewSet):
    queryset = ModelBase.permitted.all()
    serializer_class = ModelBaseSerializer


def register(router, mapping=None):
    """Register all viewsets known to app, overriding any items already
    registered with the same name."""

    if mapping is None:
        mapping =  (
            ("jmbo-modelbase-permitted", ModelBasePermittedViewSet),
            ("jmbo-modelbase", ModelBaseObjectsViewSet)
        )

    for pth, klass in mapping:
        keys = [tu[0] for tu in router.registry]
        try:
            i = keys.index(pth)
            del router.registry[i]
        except ValueError:
            pass
        # Leave default handling intact until view_name issues are resolved
        router.register(
            r"%s" % pth,
            klass
        )
        # Provide a base_name to consider app_label as well
        router.register(
            r"%s" % pth,
            klass,
            base_name=pth
        )
