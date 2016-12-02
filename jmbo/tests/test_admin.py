import unittest

from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.test.client import Client, RequestFactory

from photologue.models import PhotoSizeCache

from jmbo.tests.models import TestModel


class AdminTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.request = RequestFactory()
        cls.client = Client()

        # Editor
        cls.editor = get_user_model().objects.create(
            username="editor",
            email="editor@test.com",
            is_superuser=True,
            is_staff=True
        )
        cls.editor.set_password("password")
        cls.editor.save()
        cls.client.login(username='editor', password='password')

        cls.obj = TestModel(title="title")
        cls.obj.save()

        call_command("load_photosizes")
        PhotoSizeCache().reset()

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
