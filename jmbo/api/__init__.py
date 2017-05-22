import json
import logging

from django.conf import settings
from django.utils.encoding import filepath_to_uri

from rest_framework import viewsets
from rest_framework.serializers import HyperlinkedModelSerializer, \
    ReadOnlyField, Serializer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import DjangoModelPermissions, \
    DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.reverse import reverse
from rest_framework_extras.serializers import FormMixin
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from photologue.models import PhotoSize

from jmbo.models import ModelBase, Image
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
        fields = "__all__"

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


class ModelBaseObjectsViewSet(viewsets.ModelViewSet):
    queryset = ModelBase.objects.all().prefetch_related(
        "categories", "sites", "layers", "tags", "images"
        ).select_related("owner", "content_type", "primary_category")
    serializer_class = ModelBaseSerializer
    authentication_classes = (
        SessionAuthentication, BasicAuthentication, JSONWebTokenAuthentication
    )
    permission_classes = (DjangoModelPermissions,)

    @detail_route(methods=["post"])
    def publish(self, request, pk, **kwargs):
        self.get_object().publish()
        return Response({"status": "success"})

    @detail_route(methods=["post"])
    def unpublish(self, request, pk, **kwargs):
        self.get_object().unpublish()
        return Response({"status": "success"})


class ModelBasePermittedViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ModelBase.permitted.all().prefetch_related(
        "categories", "sites", "layers", "tags", "images"
        ).select_related("owner", "content_type", "primary_category")
    serializer_class = ModelBaseSerializer


class ImageSerializer(HyperlinkedModelSerializer):

    class Meta:
        model = Image
        fields = "__all__"


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    authentication_classes = (
        SessionAuthentication, BasicAuthentication, JSONWebTokenAuthentication
    )
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)

    @detail_route(methods=["get"])
    def scales(self, request, pk, **kwargs):
        """Return link to a view that will redirect to the scaled image. This
        intermediary view is required because we usually create the scaled
        images lazily."""

        li = []
        obj = self.get_object()
        for photosize in PhotoSize.objects.all():
            url = request.build_absolute_uri(reverse(
                "jmbo:image-scale-url",
                (obj.pk, photosize.name),
            ))
            li.append(url)
        return Response(li)


def register(router, mapping=None):
    """Register all viewsets known to app, overriding any items already
    registered with the same name."""

    if mapping is None:
        mapping =  (
            ("jmbo-modelbase-permitted", ModelBasePermittedViewSet),
            ("jmbo-modelbase", ModelBaseObjectsViewSet),
            ("jmbo-image", ImageViewSet)
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
