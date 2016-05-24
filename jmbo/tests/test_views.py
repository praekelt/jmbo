import unittest

from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.test.client import Client, RequestFactory
from django.conf import settings

from jmbo.models import ModelBase


class ViewsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.request = RequestFactory()
        cls.client = Client()

        cls.web_site = Site(id=1, domain="web.address.com", name="web.address.com")
        cls.web_site.save()

        cls.obj = ModelBase.objects.create(title="title1")
        cls.obj.sites = Site.objects.all()
        cls.obj.save()
        cls.obj.publish()

    def test_detail_view(self):
        url = self.obj.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.failUnless("""<div class="jmbo-detail jmbo-detail jmbo-modelbase-detail""" in response.content)

    def test_list_view(self):
        url = reverse("jmbo-modelbase-list", args=["jmbo", "modelbase"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.failUnless("""<div class="jmbo-list""" in response.content)
        self.failUnless("""<div class="jmbo-view-modifier">""" in response.content)

    @classmethod
    def tearDownClass(cls):
        Site.objects.all().delete()
