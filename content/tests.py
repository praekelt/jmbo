import unittest
from datetime import datetime

from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from content.admin import ModelBaseAdmin
from content.models import ModelBase
from content.utils.tests import RequestFactory


class UtilsTestCase(unittest.TestCase):

    def test_set_slug(self):
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

class ModelBaseTestCase(unittest.TestCase):
    def test_save(self):
        before_save = datetime.now()

        # created field should be set on save
        obj = ModelBase()
        obj.save()
        
        # created field should be set to current datetime on save
        after_save = datetime.now()
        self.failIf(obj.created > after_save or obj.created < before_save)

        # if a user supplies a created date use that instead of the current datetime
        test_datetime = datetime(2008, 10, 10, 12, 12)
        obj = ModelBase(created=test_datetime)
        obj.save()
        self.failIf(obj.created != test_datetime)

        # modified should be set to current datetime on each save
        before_save = datetime.now()
        obj = ModelBase()
        obj.save()
        after_save = datetime.now()
        self.failIf(obj.modified > after_save or obj.modified < before_save)

class ModelBaseAdminTestCase(unittest.TestCase):
    def test_save_model(self):
        # setup mock objects
        admin_obj = ModelBaseAdmin(ModelBase, 1)
        request = RequestFactory()
        user = User(username='test', email='test@test.com')
        user.save()
        request.user = user

        # after admin save the object's owner should be the current user 
        obj = ModelBase()
        admin_obj.save_model(request, obj, admin_obj.form, 1)
        self.failUnless(obj.owner == user)
        obj.save()
       
        # if a different user is specified as owner set that user as owner
        user = User(username='test2', email='test@test.com')
        user.save()
        
        form = admin_obj.get_form({'owner': user.id})

        import pdb; pdb.set_trace()
        admin_obj.save_model(request, obj, admin_obj.get_form({'owner': user.id}), 1)
        self.failUnless(obj.owner == user)
