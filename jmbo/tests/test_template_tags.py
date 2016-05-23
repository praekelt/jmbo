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

    def test_jmbocache(self):
        from django.conf import settings

        # Caching on same site
        t = template.Template("""{% load jmbo_template_tags %}\
            {% jmbocache 1200 "test_jmbocache" %}1{% endjmbocache %}"""
        )
        result1 = t.render(self.context)
        t = template.Template("""{% load jmbo_template_tags %}\
            {% jmbocache 1200 "test_jmbocache" %}2{% endjmbocache %}"""
        )
        result2 = t.render(self.context)
        self.failUnlessEqual(result1, result2)

        # Caching on different sites
        t = template.Template("""{% load jmbo_template_tags %}\
            {% jmbocache 1200 "test_jmbocache" %}1{% endjmbocache %}"""
        )
        result1 = t.render(self.context)
        settings.SITE_ID = 2
        Site.objects.clear_cache()
        t = template.Template("""{% load jmbo_template_tags %}\
            {% jmbocache 1200 "test_jmbocache" %}2{% endjmbocache %}"""
        )
        result2 = t.render(self.context)
        settings.SITE_ID = 2
        Site.objects.clear_cache()
        self.failIfEqual(result1, result2)

        # Check that undefined variables do not break caching
        t = template.Template("""{% load jmbo_template_tags %}\
            {% jmbocache 1200 "test_jmbocache_undefined" aaa %}1{% endjmbocache %}"""
        )
        result1 = t.render(self.context)
        t = template.Template("""{% load jmbo_template_tags %}\
            {% jmbocache 1200 "test_jmbocache_undefined" bbb %}2{% endjmbocache %}"""
        )
        result2 = t.render(self.context)
        self.failUnlessEqual(result1, result2)

        # Check that translation proxies are valid variables
        t = template.Template("""{% load jmbo_template_tags %}\
            {% jmbocache 1200 "test_jmbocache_xlt" _("aaa") %}1{% endjmbocache %}"""
        )
        result1 = t.render(self.context)
        t = template.Template("""{% load jmbo_template_tags %}\
            {% jmbocache 1200 "test_jmbocache_xlt" _("aaa") %}2{% endjmbocache %}"""
        )
        result2 = t.render(self.context)
        self.failUnlessEqual(result1, result2)

        # Check that large integer variables do not break caching
        t = template.Template("""{% load jmbo_template_tags %}\
            {% jmbocache 1200 "test_jmbocache_large" 565417614189797377 %}1{% endjmbocache %}"""
        )
        result1 = t.render(self.context)
        t = template.Template("""{% load jmbo_template_tags %}\
            {% jmbocache 1200 "test_jmbocache_large" 565417614189797377 %}2{% endjmbocache %}"""
        )
        result2 = t.render(self.context)
        self.failUnlessEqual(result1, result2)

    @classmethod
    def tearDownClass(cls):
        Site.objects.all().delete()
        settings.SITE_ID = 1
