import random
import unittest
from datetime import datetime, timedelta

from django import template
from django.db import models
from django.conf import settings
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.template import Template
from django.template.defaultfilters import slugify

from content.admin import ModelBaseAdmin
from content.filters import IntervalFilter, OrderFilter
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
       
    def test_get_poly_size(self):
        # if we have a ModelBase object, the size for content modelbase should be returned
        obj = ModelBase(title='title')
        obj.save()
        poly_size = obj._get_poly_size('test')
        self.failUnlessEqual(poly_size, 'content_modelbase_test')

        # if we have a BranchModel object without a size defined for it, the size for content modelbase should be returned
        obj = BranchModel(title='title', image='test')
        obj.save()
        poly_size = obj._get_poly_size('test')
        self.failUnlessEqual(poly_size, 'content_modelbase_test')
        
        # if we have a BranchModel object without a size defined for it, but a size has been defined for its base model TrunkModel, the size for content trunkmodel should be returned
        PhotoSize(name='content_trunkmodel_test').save()
        poly_size = obj._get_poly_size('test')
        self.failUnlessEqual(poly_size, 'content_trunkmodel_test')
        
        # if we have a BranchModel object with a size defined for it, the size for content branchmodel should be returned
        PhotoSize(name='content_branchmodel_test').save()
        poly_size = obj._get_poly_size('test')
        self.failUnlessEqual(poly_size, 'content_branchmodel_test')
        

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
        self.failUnless(staging_obj in queryset)
        settings.STAGING = True
        queryset = ModelBase.permitted.all()
        self.failIf(staging_obj in queryset)
        
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

class IntervalFilterTestCase(unittest.TestCase):
    def setUp(self):
        # generate some content, with each object created on a different date
        count = 100
        created = datetime.now() - timedelta(days=count/2)
        for i in range(0,count):
            ModelBase(title="ModelBase %s Title" % i, created=created).save()
            created += timedelta(days=1)

    def test_filter(self):
        # filter on week
        qs = ModelBase.objects.all()
        interval_filter = IntervalFilter(name="created")
        filtered_qs = interval_filter.filter(qs, 'week')
        
        # the filtered qs should contain some objects
        self.failUnless(filtered_qs.count())


        # we are filtering on week so the queryset should contain no 
        # items created prior to the last 7 days
        week_cutoff = datetime.now() - timedelta(days=7)
        for obj in filtered_qs:
            self.failIf(obj.created.date() < week_cutoff.date())
        
        # filter on month
        qs = ModelBase.objects.all()
        interval_filter = IntervalFilter(name="created")
        filtered_qs = interval_filter.filter(qs, 'month')
        
        # the filtered qs should contain some objects
        self.failUnless(filtered_qs.count())

        # we are filtering on month so the queryset should contain no 
        # items created in a prior month
        month_cutoff = datetime.today()
        month_cutoff = datetime(month_cutoff.year, month_cutoff.month, 1)
        for obj in filtered_qs:
            self.failIf(obj.created.date() < month_cutoff.date())

        # return original queryset in case of bogus value
        qs = ModelBase.objects.all()
        interval_filter = IntervalFilter(name="created")
        filtered_qs = interval_filter.filter(qs, 'bogus')
        self.failUnlessEqual(qs, filtered_qs)

class OrderFilterTestCase(unittest.TestCase):
    def setUp(self):
        # generate some content, with each object created on a different date
        # and with different vote counts
        content_count = 60
        voter_count = 10
        created = datetime.now() - timedelta(days=content_count/2)
        voters = []
        # create voting user
        for i in range(0, voter_count):
            voters.append(User.objects.get_or_create(username='voter%s' % i, email='voter%s@dress.com' % i)[0])

        for i in range(0,content_count):
            # create object
            obj = ModelBase(title="ModelBase %s Title" % i, created=created)
            obj.save()

        # vote for a sample of voters
        for obj in ModelBase.objects.all():
            for voter in random.sample(voters, random.randint(0, voter_count)):
                obj.add_vote(voter.username, +1)
                #Vote.objects.record_vote(obj, voter, 1)
                
            created += timedelta(days=1)
            
    def test_filter(self):
        # order by most recent
        qs = ModelBase.objects.all()
        order_filter = OrderFilter(name="created")
        filtered_qs = order_filter.filter(qs, 'most-recent')
        
        # the filtered qs should contain some objects
        self.failUnless(filtered_qs.count())

        # we are ordering by most recent so the queryset should be ordered by created, descending
        prev_obj = filtered_qs[0]
        for obj in filtered_qs:
            self.failIf(obj.created > prev_obj.created)
        
        # order by most liked
        qs = ModelBase.objects.all()
        order_filter = OrderFilter(name="created")
        filtered_qs = order_filter.filter(qs, 'most-liked')
        
        # the filtered qs should contain some objects
        self.failUnless(filtered_qs.count())
        
        # we are ordering by most liked so the queryset should be ordered by vote score, descending
        prev_obj = filtered_qs[0]
        for obj in filtered_qs:
            self.failIf(obj.vote_total > prev_obj.vote_total)
            prev_obj = obj
        
        # return original queryset in case of bogus value
        qs = ModelBase.objects.all()
        order_filter = OrderFilter(name="created")
        filtered_qs = order_filter.filter(qs, 'bogus')
        self.failUnlessEqual(qs, filtered_qs)
