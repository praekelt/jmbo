from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import RequestFactory

from jmbo.models import ModelBase
from jmbo.admin import ModelBaseAdmin

from jmbo.tests.models import DummyModel


class ModelBaseAdminTestCase(TestCase):
    fixtures = ["sites.json"]

    @classmethod
    def setUpTestData(cls):
        super(ModelBaseAdminTestCase, cls).setUpTestData()
        cls.user, cls.created = get_user_model().objects.get_or_create(
            username="test",
            email="test@test.com"
        )

    def test_field_hookup(self):
        model_admin = ModelBaseAdmin(DummyModel, AdminSite())

        # Field additions should be added to first fieldsets" fields
        self.failIf("test_editable_field" not in model_admin.\
                fieldsets[0][1]["fields"])
        self.failIf("test_foreign_field" not in model_admin.\
                fieldsets[0][1]["fields"])
        self.failIf("test_many_field" not in model_admin.\
                fieldsets[0][1]["fields"])

        # Non editable field additions should not be added to fieldsets
        self.failIf("test_non_editable_field" in \
                model_admin.fieldsets[0][1]["fields"])

        # Non field class members should not be added to fieldsets
        self.failIf("test_member" in model_admin.fieldsets[0][1]["fields"])

    def test_save_model(self):
        # Setup mock objects
        admin_obj = ModelBaseAdmin(ModelBase, 1)
        request = RequestFactory().get("/")
        request.user = self.user

        # After admin save the object's owner should be the current user.
        obj = ModelBase()
        admin_obj.save_model(request, obj, admin_obj.form, 1)
        self.failUnless(obj.owner == self.user)
        obj.save()

        # TODO: If a different user is specified as
        # owner set that user as owner.
