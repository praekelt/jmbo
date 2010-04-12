import unittest

from django.template.defaultfilters import slugify

from content.models import ModelBase

class ModelBaseTestCase(unittest.TestCase):

    def test_save_slug(self):
        # on save a slug should be set
        obj = ModelBase()
        obj.save()
        self.failIf(obj.slug=='')

        # in case no title is provided slug should fallback to id
        self.failUnless(obj.slug==str(obj.id))

        # in case title is probvided, slug should become sluggified version of title
        obj = ModelBase(title='title 1')
        obj.save()
        self.failUnless(obj.slug==slugify(obj.title))

        # no two items should have the same slug
        obj = ModelBase(title='title 1')
        obj.save()

        # in case an object title is updated, the slug should also be updated
        obj.title = "updated title"
        obj.save()
        self.failUnless(obj.slug==slugify(obj.title))

        # make sure the slug is actually saved
        obj = ModelBase.objects.get(id=obj.id)
        self.failIf(obj.slug=='')
