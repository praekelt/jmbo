from jmbo import api as jmbo_api

from jmbo.tests.models import TestModel


class HyperlinkedTestModelSerializer(jmbo_api.HyperlinkedModelBaseSerializer):

    class Meta(jmbo_api.HyperlinkedModelBaseSerializer.Meta):
        model = TestModel


class TestModelObjectsViewSet(jmbo_api.ModelBaseObjectsViewSet):
    queryset = TestModel.objects.all()
    serializer_class = HyperlinkedTestModelSerializer


class TestModelPermittedViewSet(jmbo_api.ModelBasePermittedViewSet):
    queryset = TestModel.permitted.all()
    serializer_class = HyperlinkedTestModelSerializer
