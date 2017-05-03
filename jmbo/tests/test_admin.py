from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase

from photologue.models import PhotoSizeCache

from jmbo.tests.models import TestModel


class AdminTestCase(TestCase):
    fixtures = ["sites.json"]

    @classmethod
    def setUpTestData(cls):
        super(AdminTestCase, cls).setUpTestData()

        # Editor
        cls.editor = get_user_model().objects.create(
            username="editor",
            email="editor@test.com",
            is_superuser=True,
            is_staff=True
        )
        cls.editor.set_password("password")
        cls.editor.save()

        cls.obj = TestModel(title="title")
        cls.obj.save()

        call_command("load_photosizes")
        PhotoSizeCache().reset()

    def setUp(self):
        super(AdminTestCase, self).setUp()
        self.client.login(username='editor', password='password')

    def test_change_list(self):
        response = self.client.get(reverse("admin:tests_testmodel_changelist"))
        self.assertEqual(response.status_code, 200)

    def test_add(self):
        response = self.client.get(reverse("admin:tests_testmodel_add"))
        self.assertEqual(response.status_code, 200)

    def test_publish_ajax(self):
        response = self.client.get(
            reverse("admin:jmbo-publish-ajax"),
            {"id": self.obj.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "published")

    def test_unpublish_ajax(self):
        response = self.client.get(
            reverse("admin:jmbo-unpublish-ajax"),
            {"id": self.obj.id}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "unpublished")

    def test_autosave_ajax(self):
        response = self.client.post(
            reverse("admin:jmbo-autosave-ajax"),
            {"id": self.obj.id, "title": "foo"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, "1")
        self.assertEqual(TestModel.objects.get(id=self.obj.id).title, "foo")
