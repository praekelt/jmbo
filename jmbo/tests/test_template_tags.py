import unittest

from django import template
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.test.client import Client, RequestFactory
from django.conf import settings

from jmbo.tests.models import BranchModel, LeafModel, TestModel


class TemplateTagsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.request = RequestFactory()
        cls.request.method = "GET"
        cls.request._path = "/"
        cls.request.get_full_path = lambda: cls.request._path
        cls.client = Client()

        # Add a site
        site, dc = Site.objects.get_or_create(id=1, name="another", domain="another.com")

    def setUp(self):
        obj = TestModel(title="title", state="published")
        obj.save()
        self.context = template.Context({
            "object": obj,
            "request": self.request
        })

    @classmethod
    def tearDownClass(cls):
        Site.objects.all().delete()
        settings.SITE_ID = 1
