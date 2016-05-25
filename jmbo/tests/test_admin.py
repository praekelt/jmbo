import unittest

from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.test.client import Client, RequestFactory


class ModelBaseTestCase(unittest.TestCase):

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

    def test_add(self):
        self.client.login(username='editor', password='password')
        response = self.client.get(reverse("admin:tests_testmodel_add"))
        self.assertEqual(response.status_code, 200)
