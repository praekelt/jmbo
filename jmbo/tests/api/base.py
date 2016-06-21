from jmbo.api import base

from jmbo.tests.models import TestModel


class HyperlinkedTestModelSerializer(base.HyperlinkedModelBaseSerializer):

    class Meta(base.HyperlinkedModelBaseSerializer.Meta):
        model = TestModel


class TestModelObjectsViewSet(base.ModelBaseObjectsViewSet):
    queryset = TestModel.objects.all()
    serializer_class = HyperlinkedTestModelSerializer


class TestModelPermittedViewSet(base.ModelBasePermittedViewSet):
    queryset = TestModel.permitted.all()
    serializer_class = HyperlinkedTestModelSerializer
