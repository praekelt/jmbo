import unittest

from django import template
from django.contrib.auth.models import User
from django.test.client import Client, RequestFactory

from jmbo.tests.models import BranchModel, LeafModel, TestModel


class InclusionTagsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.request = RequestFactory()
        cls.request.method = "GET"
        cls.request._path = "/"
        cls.request.get_full_path = lambda: cls.request._path
        class User():
            def is_authenticated(self):
                return False
        cls.request.user = User()
        cls.request.secretballot_token = "test_token"

        cls.obj1 = TestModel(title="title 1", state="published")
        cls.obj1.save()
        cls.obj2 = BranchModel(title="title 2", state="published")
        cls.obj2.save()
        cls.obj3 = LeafModel(title="title 3", state="published")
        cls.obj3.save()

    def test_render_tag(self):
        # "%s/inclusion_tags/%s_%s.html" % (ctype.app_label, ctype.model, type)
        self.context = template.Context({"object": self.obj1})
        t = template.Template("""{% load jmbo_inclusion_tags %}\
{% render_object object "test_block" %}""")
        result = t.render(self.context)
        expected = u"TestModel block\n"
        self.failUnlessEqual(result, expected)

        # "%s/%s/inclusion_tags/object_%s.html" % (ctype.app_label, ctype.model, type),
        self.context = template.Context({"object": self.obj2})
        t = template.Template("""{% load jmbo_inclusion_tags %}\
{% render_object object "test_block" %}""")
        result = t.render(self.context)
        expected = u"BranchModel block\n"
        self.failUnless(result, expected)

        # "jmbo/inclusion_tags/modelbase_%s.html" % type
        self.context = template.Context({"object": self.obj3})
        t = template.Template("""{% load jmbo_inclusion_tags %}\
{% render_object object "test_block" %}""")
        result = t.render(self.context)
        expected = u"ModelBase block\n"
        self.failUnlessEqual(result, expected)

        # No template was found
        t = template.Template("""{% load jmbo_inclusion_tags %}\
{% render_object object "foobar" %}""")
        result = t.render(self.context)
        expected_result = u""
        self.failUnlessEqual(result, expected_result)

    def test_header_tag(self):
        """Provide a custom object_header because default has dependencies that
        require request to be annotated and it is hard to fake without an HTTP
        call"""
        self.context = template.Context({"object": self.obj1, "request": self.request})
        t = template.Template("{% load jmbo_inclusion_tags %}\
{% object_header object %}")
        result = t.render(self.context)
        self.failUnless("Object header" in result)
        self.failUnless("get_full_path = /" in result)
        self.failUnless("title = title 1" in result)

    def test_footer_tag(self):
        self.context = template.Context({"object": self.obj1, "request": self.request})
        t = template.Template("{% load jmbo_inclusion_tags %}\
{% object_footer object %}")
        result = t.render(self.context)
        self.failUnless("object-footer" in result)

    def test_comments_tag(self):
        self.context = template.Context({"object": self.obj1, "request": self.request})
        t = template.Template("{% load jmbo_inclusion_tags %}\
{% object_comments object %}")
        result = t.render(self.context)
        self.failUnless("honeypot" in result)
