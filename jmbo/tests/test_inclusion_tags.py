import os

from django import template
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.test import TestCase
from django.test.client import RequestFactory

from photologue.models import PhotoSizeCache

from jmbo.models import Image, ModelBaseImage
from jmbo.tests.models import BranchModel, LeafModel, TestModel
from jmbo.tests.extra.models import LeafModel as ExtraLeafModel


RES_DIR = os.path.join(os.path.dirname(__file__), "res")
IMAGE_PATH = os.path.join(RES_DIR, "image.jpg")


def set_image(obj):
    image = Image.objects.create(title=IMAGE_PATH)
    image.image.save(
        os.path.basename(IMAGE_PATH),
        ContentFile(open(IMAGE_PATH, "rb").read())
    )
    ModelBaseImage.objects.create(modelbase=obj, image=image)


class InclusionTagsTestCase(TestCase):
    fixtures = ["sites.json"]

    @classmethod
    def setUpTestData(cls):
        super(InclusionTagsTestCase, cls).setUpTestData()

        cls.request = RequestFactory().get("/")
        class User():
            def is_authenticated(self):
                return False
        cls.request.user = User()
        cls.request.secretballot_token = "test_token"

        cls.obj1 = TestModel(title="title 1", state="published")
        cls.obj1.save()
        set_image(cls.obj1)
        cls.obj2 = BranchModel(title="title 2", state="published")
        cls.obj2.save()
        cls.obj3 = LeafModel(title="title 3", state="published")
        cls.obj3.save()
        cls.obj4 = ExtraLeafModel(title="title 4", state="published")
        cls.obj4.save()

        call_command("load_photosizes")
        PhotoSizeCache().reset()

    def test_render_object_tag(self):
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

        # LeafModel subclasses BranchModel and does not have its own detail
        # template, thus it traverses upwards until a parent class provides a
        # detail template.
        self.context = template.Context({"object": self.obj3})
        t = template.Template("""{% load jmbo_inclusion_tags %}\
{% render_object object "test_block" %}""")
        result = t.render(self.context)
        expected = u"BranchModel block\n"
        self.failUnlessEqual(result, expected)

        # "%s/inclusion_tags/%s_%s.html" % (ctype.app_label, ctype.model, type)
        self.context = template.Context({"object": self.obj4})
        t = template.Template("""{% load jmbo_inclusion_tags %}\
{% render_object object "test_block" %}""")
        result = t.render(self.context)
        expected = u"ExtraLeafModel block\n"
        self.failUnlessEqual(result, expected)

        # No template was found
        t = template.Template("""{% load jmbo_inclusion_tags %}\
{% render_object object "foobar" %}""")
        result = t.render(self.context)
        expected_result = u""
        self.failUnlessEqual(result, expected_result)

    def test_header_tag(self):
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
        self.failUnless("footer-inclusion" in result)

    def test_comments_tag(self):
        self.context = template.Context({"object": self.obj1, "request": self.request})
        t = template.Template("{% load jmbo_inclusion_tags %}\
{% object_comments object %}")
        result = t.render(self.context)
        self.failUnless("honeypot" in result)

    def test_render_tag_inherits_context(self):
        """The render tag must have access to the existing context"""
        self.context = template.Context({"object": self.obj1, "request": self.request})
        t = template.Template("{% load jmbo_inclusion_tags tests_template_tags %}\
{% inject_foo %}\
{% object_header object %}")
        result = t.render(self.context)
        self.failUnless("foo = bar" in result)

    def test_image_url_tag(self):
        self.context = template.Context({"object": self.obj1})
        t = template.Template("""{% load jmbo_inclusion_tags %}\
{% image_url object "detail" %}""")
        result = t.render(self.context)
        self.failUnless("jmbo_modelbase_detail.jpg" in result)

