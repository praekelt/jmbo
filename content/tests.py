import random
import unittest
from datetime import datetime, timedelta

from django import template
from django.conf import settings
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ViewDoesNotExist
from django.core.urlresolvers import reverse
from django.db import models
from django.template import Template
from django.template.defaultfilters import slugify
from django.test import TestCase
from django.test.client import Client

from content.admin import ModelBaseAdmin
from content.models import ModelBase
from content.utils.tests import RequestFactory
        
from photologue.models import PhotoSize
from secretballot.models import Vote
        
       
class DummyRelationalModel1(models.Model):
    pass
models.register_models('content', DummyRelationalModel1)
class DummyRelationalModel2(models.Model):
    pass
models.register_models('content', DummyRelationalModel2)
class DummyModel(ModelBase):
    test_editable_field = models.CharField(max_length=32)
    test_non_editable_field = models.CharField(max_length=32, editable=False)
    test_foreign_field = models.ForeignKey('DummyRelationalModel1', blank=True, null=True,)
    test_many_field = models.ManyToManyField('DummyRelationalModel2')
    test_member = True
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
class TestModel(ModelBase):
    pass
models.register_models('content', TestModel)

class UtilsTestCase(unittest.TestCase):
    def test_generate_slug(self):
        # on save a slug should be set
        obj = ModelBase(title='utils test case title')
        obj.save()
        self.failIf(obj.slug=='')

        # slug should become sluggified version of title
        obj = ModelBase(title='utils test case title 1')
        obj.save()
        self.failUnless(obj.slug==slugify(obj.title))

        # no two items should have the same slug
        obj = ModelBase(title='utils test case title 1')
        obj.save()

        # in case an object title is updated, the slug should also be updated
        obj.title = "updated title"
        obj.save()
        self.failUnless(obj.slug==slugify(obj.title))
        
        # in case an object is updated, without the title being changed, the slug should remain unchanged
        orig_slug = obj.slug
        obj.save()
        self.failUnless(obj.slug==orig_slug)

        # make sure the slug is actually saved
        obj = ModelBase.objects.get(id=obj.id)
        self.failIf(obj.slug=='')

class ModelBaseTestCase(unittest.TestCase):
    def test_save(self):
        before_save = datetime.now()

        # created field should be set on save
        obj = ModelBase(title='title')
        obj.save()
        
        # created field should be set to current datetime on save
        after_save = datetime.now()
        self.failIf(obj.created > after_save or obj.created < before_save)

        # if a user supplies a created date use that instead of the current datetime
        test_datetime = datetime(2008, 10, 10, 12, 12)
        obj = ModelBase(title='title', created=test_datetime)
        obj.save()
        self.failIf(obj.created != test_datetime)

        # modified should be set to current datetime on each save
        before_save = datetime.now()
        obj = ModelBase(title='title')
        obj.save()
        after_save = datetime.now()
        self.failIf(obj.modified > after_save or obj.modified < before_save)

        # leaf class content type should be set on save
        obj = DummyModel(title='title')
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
        obj = LeafModel(title='title')
        obj.save()

        # always return the leaf class, no matter where we are in the hierarchy
        self.failUnless(TrunkModel.objects.get(slug=obj.slug).as_leaf_class() == obj)
        self.failUnless(BranchModel.objects.get(slug=obj.slug).as_leaf_class() == obj)
        self.failUnless(LeafModel.objects.get(slug=obj.slug).as_leaf_class() == obj)

    def test_vote_total(self):
        # create object with some votes
        obj = ModelBase(title='title')
        obj.save()
        obj.add_vote("token1", 1)
        obj.add_vote("token2", -1)
        obj.add_vote("token3", 1)

        # vote_total should return an integer
        result = obj.vote_total
        self.failUnlessEqual(result.__class__, int)

        # vote total is calculated as total_upvotes - total_downvotes
        self.failUnlessEqual(result, 1)

    def test_is_permitted(self):
        # create website site item and set as current site
        web_site = Site(domain="web.address.com")
        web_site.save()
        settings.SITE_ID = web_site.id

        # create unpublished item
        unpublished_obj = ModelBase(title='title', state='unpublished')
        unpublished_obj.save()
        unpublished_obj.sites.add(web_site)
        unpublished_obj.save()
        
        # create published item
        published_obj = ModelBase(title='title', state='published')
        published_obj.save()
        published_obj.sites.add(web_site)
        published_obj.save()
        
        # create staging item
        staging_obj = ModelBase(title='title', state='staging')
        staging_obj.save()
        staging_obj.sites.add(web_site)
        staging_obj.save()
        
        # is_permitted should be False for unpublished objects
        self.failIf(unpublished_obj.is_permitted)

        # is_permitted should be True for published objects
        self.failUnless(published_obj.is_permitted)
        
        # is_permitted should be True for otherwise published objects in the staging state for instances that define settings.STAGING = True
        settings.STAGING = False
        self.failIf(staging_obj.is_permitted)
        settings.STAGING = True
        self.failUnless(staging_obj.is_permitted)
        
        # is_permitted should be True only if the object is published for the current site
        published_obj_web = ModelBase(state='published')
        published_obj_web.save()
        published_obj_web.sites.add(web_site)
        published_obj_web.save()
        self.failUnless(published_obj_web.is_permitted)
        
        # is_permitted should be False if the object is not published for the current site
        mobile_site = Site(domain="mobi.address.com")
        mobile_site.save()
        published_obj_mobile = ModelBase(state='published')
        published_obj_mobile.save()
        published_obj_mobile.sites.add(mobile_site)
        published_obj_mobile.save()
        self.failIf(published_obj_mobile.is_permitted)

class ModelBaseAdminTestCase(unittest.TestCase):
    def setUp(self):
        self.user, self.created = User.objects.get_or_create(username='test', email='test@test.com')
   
    def test_field_hookup(self):
        model_admin = ModelBaseAdmin(DummyModel, AdminSite())
        
        # field additions should be added to first fieldsets' fields
        self.failIf('test_editable_field' not in model_admin.fieldsets[0][1]['fields'])
        self.failIf('test_foreign_field' not in model_admin.fieldsets[0][1]['fields'])
        self.failIf('test_many_field' not in model_admin.fieldsets[0][1]['fields'])
        
        # non editable field additions should not be added to fieldsets
        self.failIf('test_non_editable_field' in model_admin.fieldsets[0][1]['fields'])

        # non field class members should not be added to fieldsets
        self.failIf('test_member' in model_admin.fieldsets[0][1]['fields'])

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
    def setUp(self):
        # create website site item and set as current site
        self.web_site = Site(domain="web.address.com")
        self.web_site.save()
        settings.SITE_ID = self.web_site.id

    def test_get_query_set(self):
        # create unpublished item
        unpublished_obj = ModelBase(title='title', state='unpublished')
        unpublished_obj.save()
        unpublished_obj.sites.add(self.web_site)
        unpublished_obj.save()
        
        # create published item
        published_obj = ModelBase(title='title', state='published')
        published_obj.save()
        published_obj.sites.add(self.web_site)
        published_obj.save()
        
        # create staging item
        staging_obj = ModelBase(title='title', state='staging')
        staging_obj.save()
        staging_obj.sites.add(self.web_site)
        staging_obj.save()
        
        # unpublished objects should not be available in queryset
        queryset = ModelBase.permitted.all()
        self.failIf(unpublished_obj in queryset)

        # published objects should always be available in queryset
        self.failUnless(published_obj in queryset)
        
        # staging objects should only be available on instances that define settings.STAGING = True
        settings.STAGING = False
        queryset = ModelBase.permitted.all()
        self.failIf(staging_obj in queryset)
        settings.STAGING = True
        queryset = ModelBase.permitted.all()
        self.failUnless(staging_obj in queryset)
        
        # queryset should only contain items for the current site
        published_obj_web = ModelBase(state='published')
        published_obj_web.save()
        published_obj_web.sites.add(self.web_site)
        published_obj_web.save()
        queryset = ModelBase.permitted.all()
        self.failUnless(published_obj_web in queryset)
        
        # queryset should not contain items for other sites
        mobile_site = Site(domain="mobi.address.com")
        mobile_site.save()
        published_obj_mobile = ModelBase(state='published')
        published_obj_mobile.save()
        published_obj_mobile.sites.add(mobile_site)
        published_obj_mobile.save()
        queryset = ModelBase.permitted.all()
        self.failIf(published_obj_mobile in queryset)

    def test_content_type(self):
        obj = BranchModel(title='title', state='published')
        obj.save()
        obj.sites.add(self.web_site)
        obj.save()

        # queryset should return objects of the same type as the queried model
        queryset = BranchModel.permitted.all()
        self.failUnless(obj in queryset)
        queryset = ModelBase.permitted.all()
        self.failIf(obj in queryset)

class InclusionTagsTestCase(unittest.TestCase):
    def setUp(self):
        obj = TestModel(title='title', state='published')
        obj.save()
        self.context = template.Context({'object': obj})

    def test_render_tag(self):
        # load correct template for provided object and type
        t = Template("{% load content_inclusion_tags %}{% render_object object block %}")
        result = t.render(self.context)
        expected_result = u'Test string for testing purposes\n'
        self.failUnlessEqual(result, expected_result)

        # if template is not available for object, fall back to default content template
        obj = BranchModel(title='title', state='published')
        obj.save()
        self.context = template.Context({'object': obj})
        t = Template("{% load content_inclusion_tags %}{% render_object object block %}")
        result = t.render(self.context)
        self.failUnless(result)

        # return the empty string if no template can be found for the given type for either obj or content.
        t = Template("{% load content_inclusion_tags %}{% render_object object foobar %}")
        result = t.render(self.context)
        expected_result = u''
        self.failUnlessEqual(result, expected_result)

class TemplateTagsTestCase(unittest.TestCase):
    def setUp(self):
        def url_callable(obj):
            return 'Test URL method using object %s' % obj.__class__.__name__

        obj = TestModel(title='title', state='published')
        obj.save()
        self.context = template.Context({'object': obj, 'url_callable': url_callable})

    def test_smart_url(self):
        # return method call with result based on object provided
        t = Template("{% load content_template_tags %}{% smart_url url_callable object %}")
        result = t.render(self.context)
        self.failUnlessEqual(result, 'Test URL method using object TestModel') 
