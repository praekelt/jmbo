from jmbo import api as jmbo_api

from jmbo.tests.models import TestModel


class TestModelSerializer(jmbo_api.ModelBaseSerializer):

    class Meta(jmbo_api.ModelBaseSerializer.Meta):
        model = TestModel

    def get_extra_kwargs(self):
        # We specify a base_name at router registration and this is a way to
        # sneak in view_name so it resolves properly.
        di = super(TestModelSerializer, self).get_extra_kwargs()
        #import pdb;pdb.set_trace()
        if isinstance(self.context["view"], jmbo_api.ModelBasePermittedViewSet):
            di["url"] = {"view_name": "tests-testmodel-permitted-detail"}
        else:
            di["url"] = {"view_name": "tests-testmodel-detail"}
        return di

class TestModelObjectsViewSet(jmbo_api.ModelBaseObjectsViewSet):
    queryset = TestModel.objects.all()
    serializer_class = TestModelSerializer


class TestModelPermittedViewSet(jmbo_api.ModelBasePermittedViewSet):
    queryset = TestModel.permitted.all()
    serializer_class = TestModelSerializer


def register(router):
    return jmbo_api.register(
        router,
        (
            ("tests-testmodel-permitted", TestModelPermittedViewSet),
            ("tests-testmodel", TestModelObjectsViewSet),
        )
    )
