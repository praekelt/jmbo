from django.template.defaultfilters import slugify
from django.test import TestCase

from jmbo.models import ModelBase


class UtilsTestCase(TestCase):
    fixtures = ["sites.json"]

    def test_generate_slug(self):
        # On save a slug should be set
        obj = ModelBase(title="utils test case title")
        obj.save()
        self.failIf(obj.slug == "")

        # Slug should become sluggified version of title
        obj = ModelBase(title="utils test case title 1")
        obj.save()
        self.failUnless(obj.slug == slugify(obj.title))

        # No two items should have the same slug
        obj = ModelBase(title="utils test case title 1")
        obj.save()

        # In case an object title is updated, the slug not be updated
        obj.title = "updated title"
        obj.save()
        self.failIf(obj.slug == slugify(obj.title))

        # In case an object is updated, without the title being changed
        # the slug should remain unchanged.
        orig_slug = obj.slug
        obj.save()
        self.failUnless(obj.slug == orig_slug)

        # Make sure the slug is actually saved
        obj = ModelBase.objects.get(id=obj.id)
        self.failIf(obj.slug == "")

        # Empty slugs might trip up regex query
        obj = ModelBase()
        obj.save()
        obj = ModelBase()
        obj.save()
        obj = ModelBase()
        obj.save()
