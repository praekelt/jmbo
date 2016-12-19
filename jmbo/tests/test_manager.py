from django.contrib.sites.models import Site
from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone

from layers.models import Layer

from jmbo.models import ModelBase
from jmbo.management.commands import jmbo_publish
from jmbo.tests.models import DummyRelationalModel1, DummyRelationalModel2, \
    DummyTargetModelBase, DummySourceModelBase, DummyModel, TrunkModel, \
    BranchModel, LeafModel, TestModel


class PermittedManagerTestCase(TestCase):
    fixtures = ["sites.json"]

    @classmethod
    def setUpClass(cls):
        super(PermittedManagerTestCase, cls).setUpClass()
        cls.web_site = Site.objects.all().first()
        cls.mobile_site = Site.objects.all().last()

    @classmethod
    def setUpTestData(cls):
        super(PermittedManagerTestCase, cls).setUpTestData()
        #call_command("load_layers")

    def test_get_queryset(self):
        # create unpublished item
        unpublished_obj = ModelBase(title="title", state="unpublished")
        unpublished_obj.save()
        unpublished_obj.sites.add(self.web_site)
        unpublished_obj.save()

        # create published item
        published_obj = ModelBase(title="title", state="published")
        published_obj.save()
        published_obj.sites.add(self.web_site)
        published_obj.save()

        # unpublished objects should not be available in queryset
        queryset = ModelBase.permitted.all()
        self.failIf(unpublished_obj in queryset)

        # published objects should always be available in queryset
        self.failUnless(published_obj in queryset)

        # queryset should only contain items for the current site
        published_obj_web = ModelBase(state="published")
        published_obj_web.save()
        published_obj_web.sites.add(self.web_site)
        published_obj_web.save()
        queryset = ModelBase.permitted.all()
        self.failUnless(published_obj_web in queryset)

        # queryset should not contain items for other sites
        published_obj_mobile = ModelBase(state="published")
        published_obj_mobile.save()
        published_obj_mobile.sites.add(self.mobile_site)
        published_obj_mobile.save()
        queryset = ModelBase.permitted.all()
        self.failIf(published_obj_mobile in queryset)

        # Publish to different layers. The current layer during this test run
        # is "web".
        with override_settings(LAYERS={"tree": ["basic", ["web"]], "current": "web"}):
            call_command("load_layers")
            obj_layer_basic = ModelBase.objects.create(state="published")
            obj_layer_basic.sites = Site.objects.all()
            obj_layer_basic.layers = [Layer.objects.get(name="basic")]
            obj_layer_basic.save()
            obj_layer_web = ModelBase.objects.create(state="published")
            obj_layer_web.sites = Site.objects.all()
            obj_layer_web.layers = [Layer.objects.get(name="web")]
            obj_layer_web.save()
            queryset = ModelBase.permitted.all()
            self.failIf(obj_layer_basic in queryset)
            self.failUnless(obj_layer_web in queryset)

    def test_publish_retract(self):
        today = timezone.make_aware(timezone.datetime.today())
        yesterday = today - timezone.timedelta(days=1)
        tomorrow = today + timezone.timedelta(days=1)

        p1 = ModelBase(title="title", state="published")
        p1.save()
        p1.sites.add(self.web_site)
        p1.save()
        jmbo_publish.Command().handle()
        queryset = ModelBase.permitted.all()
        self.failUnless(p1 in queryset)

        p2 = ModelBase(title="title", publish_on=today)
        p2.save()
        p2.sites.add(self.web_site)
        p2.save()
        jmbo_publish.Command().handle()
        queryset = ModelBase.permitted.all()
        self.failUnless(p2 in queryset)

        p4 = ModelBase(title="title", publish_on=today, retract_on=tomorrow)
        p4.save()
        p4.sites.add(self.web_site)
        p4.save()
        jmbo_publish.Command().handle()
        queryset = ModelBase.permitted.all()
        self.failUnless(p4 in queryset)

        p5 = ModelBase(title="title", publish_on=tomorrow)
        p5.save()
        p5.sites.add(self.web_site)
        p5.save()
        jmbo_publish.Command().handle()
        queryset = ModelBase.permitted.all()
        self.failIf(p5 in queryset)

        p6 = ModelBase(title="title", publish_on=yesterday, retract_on=today)
        p6.save()
        p6.sites.add(self.web_site)
        p6.save()
        jmbo_publish.Command().handle()
        queryset = ModelBase.permitted.all()
        self.failIf(p6 in queryset)

        p7 = ModelBase(title="title", publish_on=tomorrow, retract_on=tomorrow)
        p7.save()
        p7.sites.add(self.web_site)
        p7.save()
        jmbo_publish.Command().handle()
        queryset = ModelBase.permitted.all()
        self.failIf(p7 in queryset)

        p8 = ModelBase(
            title="title", publish_on=yesterday, retract_on=yesterday
        )
        p8.save()
        p8.sites.add(self.web_site)
        p8.save()
        jmbo_publish.Command().handle()
        queryset = ModelBase.permitted.all()
        self.failIf(p8 in queryset)

    def test_content_type(self):
        obj = BranchModel(title="title", state="published")
        obj.save()
        obj.sites.add(self.web_site)
        obj.save()

        # queryset should return objects of the same type as the queried model
        queryset = BranchModel.permitted.all()
        self.failUnless(obj in queryset)
        queryset = ModelBase.permitted.all()
        self.failIf(obj in queryset)

    def test_related_permitted_query(self):
        # Targets for DummyModel to point to
        dtmb_p = DummyTargetModelBase(title="dtmb_p", state="published")
        dtmb_p.save()
        dtmb_p.sites.add(self.web_site)
        dtmb_p.save()
        dtmb_up = DummyTargetModelBase(title="dtmb_up")
        dtmb_up.save()
        dtmb_up.sites.add(self.web_site)
        dtmb_up.save()

        # Dummy model - published
        dm_p = DummyModel(
            title="title",
            state="published",
            test_foreign_published=dtmb_p,
            test_foreign_unpublished=dtmb_up,
        )
        dm_p.save()
        dm_p.test_many_published.add(dtmb_p)
        dm_p.test_many_unpublished.add(dtmb_up)
        dm_p.save()

        # Dummy model - unpublished
        dm_up = DummyModel(
            title="title",
        )
        dm_up.save()

        # Source models that point at DummyModel
        # Published, points to published DummyModel
        dsmb_p = DummySourceModelBase(
            title="dsmb_p", points_to=dm_p, state="published"
        )
        dsmb_p.save()
        dsmb_p.sites.add(self.web_site)
        dsmb_p.save()

        # Unpublished, points to published DummyModel
        dsmb_up = DummySourceModelBase(
            title="dsmb_up", points_to=dm_p,
        )
        dsmb_up.save()
        dsmb_up.sites.add(self.web_site)
        dsmb_up.save()

        # Published, points to unpublished DummyModel
        dsmb_p2 = DummySourceModelBase(
            title="dsmb_p2", points_to=dm_up, state="published"
        )
        dsmb_p2.save()
        dsmb_p2.sites.add(self.web_site)
        dsmb_p2.save()
