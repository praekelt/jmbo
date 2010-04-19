import unittest
from datetime import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify

from content.admin import ModelBaseAdmin
from content.models import ModelBase
from content.utils.tests import RequestFactory
        
class DummyModel(ModelBase):
    pass
models.register_models('content', DummyModel)
class TrunkModel(ModelBase):
    pass
models.register_models('content', TrunkModel)
class BranchModel(TrunkModel):
    pass
models.register_models('content', BranchModel)
class LeafModel(BranchModel):
    pass
models.register_models('content', LeafModel)

class UtilsTestCase(unittest.TestCase):
    def setUp(self):
        self.user, self.created = User.objects.get_or_create(username='test', email='test@test.com')

    def test_set_slug(self):
        # on save a slug should be set
        obj = ModelBase(owner=self.user)
        obj.save()
        self.failIf(obj.slug=='')

        # in case no title is provided slug should fallback to id
        self.failUnless(obj.slug==str(obj.id))

        # in case title is probvided, slug should become sluggified version of title
        obj = ModelBase(title='title 1', owner=self.user)
        obj.save()
        self.failUnless(obj.slug==slugify(obj.title))

        # no two items should have the same slug
        obj = ModelBase(title='title 1', owner=self.user)
        obj.save()

        # in case an object title is updated, the slug should also be updated
        obj.title = "updated title"
        obj.save()
        self.failUnless(obj.slug==slugify(obj.title))

        # make sure the slug is actually saved
        obj = ModelBase.objects.get(id=obj.id)
        self.failIf(obj.slug=='')

class ModelBaseTestCase(unittest.TestCase):
    def setUp(self):
        self.user, self.created = User.objects.get_or_create(username='test', email='test@test.com')
        
    def test_save(self):
        before_save = datetime.now()

        # created field should be set on save
        obj = ModelBase(owner=self.user)
        obj.save()
        
        # created field should be set to current datetime on save
        after_save = datetime.now()
        self.failIf(obj.created > after_save or obj.created < before_save)

        # if a user supplies a created date use that instead of the current datetime
        test_datetime = datetime(2008, 10, 10, 12, 12)
        obj = ModelBase(created=test_datetime, owner=self.user)
        obj.save()
        self.failIf(obj.created != test_datetime)

        # modified should be set to current datetime on each save
        before_save = datetime.now()
        obj = ModelBase(owner=self.user)
        obj.save()
        after_save = datetime.now()
        self.failIf(obj.modified > after_save or obj.modified < before_save)

        # leaf class content type should be set on save
        obj = DummyModel(owner=self.user)
        obj.save()
        self.failUnless(obj.content_type == ContentType.objects.get_for_model(DummyModel))
        
        # leaf class class name should be set on save
        self.failUnless(obj.class_name == DummyModel.__name__)

        # correct leaf class content type should be retained over base class' content type
        base = obj.modelbase_ptr
        base.save()
        self.failUnless(base.content_type == ContentType.objects.get_for_model(DummyModel))
       
        # correct leaf class class name should be retained over base class' class name
        self.failUnless(base.class_name == DummyModel.__name__)

    def test_as_leaf_class(self):
        obj = LeafModel(owner=self.user)
        obj.save()

        # always return the leaf class, no matter where we are in the hierarchy
        self.failUnless(TrunkModel.objects.get(slug=obj.slug).as_leaf_class() == obj)
        self.failUnless(BranchModel.objects.get(slug=obj.slug).as_leaf_class() == obj)
        self.failUnless(LeafModel.objects.get(slug=obj.slug).as_leaf_class() == obj)

class ModelBaseAdminTestCase(unittest.TestCase):
    def setUp(self):
        self.user, self.created = User.objects.get_or_create(username='test', email='test@test.com')
    
    def test_save_model(self):
        # setup mock objects
        admin_obj = ModelBaseAdmin(ModelBase, 1)
        request = RequestFactory()
        request.user = self.user

        # after admin save the object's owner should be the current user 
        obj = ModelBase()
        admin_obj.save_model(request, obj, admin_obj.form, 1)
        self.failUnless(obj.owner == self.user)
        obj.save()
       
        # TODO: if a different user is specified as owner set that user as owner


class PermittedManagerTestCase(unittest.TestCase):
    def test_get_query_set(self):
        unpublished_obj = ModelBase(state='unpublished')
        unpublished_obj.save()
        published_obj = ModelBase(state='published')
        published_obj.save()
        staging_obj = ModelBase(state='staging')
        staging_obj.save()
        
        # unpublished objects should not be available in queryset
        queryset = ModelBase.permitted.all()
        self.failIf(unpublished_obj in queryset)

        # published objects should always be available in queryset
        self.failUnless(published_obj in queryset)
        
        # staging objects should only be available on instances that define settings.STAGING = True
        self.failUnless(staging_obj in queryset)
        settings.STAGING = True
        queryset = ModelBase.permitted.all()
        self.failIf(staging_obj in queryset)
