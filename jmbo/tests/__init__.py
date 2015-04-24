import random
import unittest
from datetime import datetime, timedelta

from django import template
from django.conf import settings
from django.contrib import comments
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
from django.contrib.gis.geos import fromstr
from django.utils import timezone
from django.core.management import call_command
from django.utils.translation import ugettext as _

from photologue.models import PhotoSize
from secretballot.models import Vote

from jmbo.admin import ModelBaseAdmin
from jmbo.models import ModelBase
from jmbo.utils.tests import RequestFactory
from jmbo.management.commands import jmbo_publish
from jmbo import USE_GIS

if USE_GIS:
    from atlas.models import Location, City, Country


class DummyRelationalModel1(models.Model):
    pass
models.register_models('jmbo', DummyRelationalModel1)


class DummyRelationalModel2(models.Model):
    pass
models.register_models('jmbo', DummyRelationalModel2)


class DummyTargetModelBase(ModelBase):
    pass
models.register_models('jmbo', DummyTargetModelBase)


class DummySourceModelBase(ModelBase):
    points_to = models.ForeignKey('DummyModel')
    points_to_many = models.ManyToManyField('DummyModel', related_name='to_many')
models.register_models('jmbo', DummySourceModelBase)


class DummyModel(ModelBase):
    test_editable_field = models.CharField(max_length=32)
    test_non_editable_field = models.CharField(max_length=32, editable=False)
    test_foreign_field = models.ForeignKey(
        'DummyRelationalModel1',
        blank=True,
        null=True
    )
    test_foreign_published = models.ForeignKey(
        'DummyTargetModelBase',
        blank=True,
        null=True,
        related_name='foreign_published'
    )
    test_foreign_unpublished = models.ForeignKey(
        'DummyTargetModelBase',
        blank=True,
        null=True,
        related_name='foreign_unpublished'
    )
    test_many_field = models.ManyToManyField('DummyRelationalModel2')
    test_many_published = models.ManyToManyField(
        'DummyTargetModelBase', related_name='many_published',
        blank=True, null=True
    )
    test_many_unpublished = models.ManyToManyField(
        'DummyTargetModelBase', related_name='many_unpublished',
        blank=True, null=True
    )
    test_member = True
models.register_models('jmbo', DummyModel)


class TrunkModel(ModelBase):
    pass
models.register_models('jmbo', TrunkModel)


class BranchModel(TrunkModel):
    pass
models.register_models('jmbo', BranchModel)


class LeafModel(BranchModel):
    pass
models.register_models('jmbo', LeafModel)


class TestModel(ModelBase):
    pass
models.register_models('jmbo', TestModel)


class UtilsTestCase(unittest.TestCase):
    def test_generate_slug(self):
        # on save a slug should be set
        obj = ModelBase(title='utils test case title')
        obj.save()
        self.failIf(obj.slug == '')

        # slug should become sluggified version of title
        obj = ModelBase(title='utils test case title 1')
        obj.save()
        self.failUnless(obj.slug == slugify(obj.title))

        # no two items should have the same slug
        obj = ModelBase(title='utils test case title 1')
        obj.save()

        # in case an object title is updated, the slug not be updated
        obj.title = "updated title"
        obj.save()
        self.failIf(obj.slug == slugify(obj.title))

        # In case an object is updated, without the title being changed
        # the slug should remain unchanged.
        orig_slug = obj.slug
        obj.save()
        self.failUnless(obj.slug == orig_slug)

        # make sure the slug is actually saved
        obj = ModelBase.objects.get(id=obj.id)
        self.failIf(obj.slug == '')

        # Empty slugs might trip up regex query.
        obj = ModelBase()
        obj.save()
        obj = ModelBase()
        obj.save()
        obj = ModelBase()
        obj.save()


class ModelBaseTestCase(unittest.TestCase):
    def test_save(self):
        before_save = timezone.now()

        # created field should be set on save
        obj = ModelBase(title='title')
        obj.save()

        # created field should be set to current datetime on save
        after_save = timezone.now()
        self.failIf(obj.created > after_save or obj.created < before_save)

        # If a user supplies a created date use that
        # instead of the current datetime.
        test_datetime = datetime(2008, 10, 10, 12, 12)
        obj = ModelBase(title='title', created=test_datetime)
        obj.save()
        self.failIf(obj.created != test_datetime)

        # modified should be set to current datetime on each save
        before_save = timezone.now()
        obj = ModelBase(title='title')
        obj.save()
        after_save = timezone.now()
        self.failIf(obj.modified > after_save or obj.modified < before_save)

        # leaf class content type should be set on save
        obj = DummyModel(title='title')
        obj.save()
        self.failUnless(obj.content_type == ContentType.objects.\
                get_for_model(DummyModel))

        # leaf class class name should be set on save
        self.failUnless(obj.class_name == DummyModel.__name__)

        # Correct leaf class content type should be retained
        # over base class' content type.
        base = obj.modelbase_ptr
        base.save()
        self.failUnless(base.content_type == ContentType.objects.\
                get_for_model(DummyModel))

        # Correct leaf class class name should be
        # retained over base class' class name.
        self.failUnless(base.class_name == DummyModel.__name__)

    def test_unique_slugs(self):
        # create 2 sites
        site_1 = Site(domain="site1.example.com")
        site_1.save()
        site_2 = Site(domain="site2.example.com")
        site_2.save()

        # Create an object for site 1
        obj_1 = ModelBase(title='object for site 1')
        obj_1.save()
        obj_1.sites.add(site_1)
        obj_1.slug = 'generic_slug'
        obj_1.save()

        # Create an object for site 2
        obj_2 = ModelBase(title='object for site 2')
        obj_2.save()
        obj_2.sites.add(site_2)
        obj_2.slug = 'generic_slug'
        obj_2.save()

        # Trying to add site_1 should raise an error.
        with self.assertRaises(RuntimeError):
            obj_2.sites.add(site_1)
            obj_2.save()

        # When the slugs differ, you can add site_1.
        obj_2.slug = 'generic_slug_2'
        obj_2.sites.add(site_1)
        obj_2.save()

        # Trying to change the slug to an existing one should raise an error.
        with self.assertRaises(RuntimeError):
            obj_2.slug = 'generic_slug'
            obj_2.save()

    def test_as_leaf_class(self):
        obj = LeafModel(title='title')
        obj.save()

        # always return the leaf class, no matter where we are in the hierarchy
        self.failUnless(TrunkModel.objects.get(slug=obj.slug).\
                as_leaf_class() == obj)
        self.failUnless(BranchModel.objects.get(slug=obj.slug).\
                as_leaf_class() == obj)
        self.failUnless(LeafModel.objects.get(slug=obj.slug).\
                as_leaf_class() == obj)

    def test_vote_total(self):
        # create object with some votes
        obj = ModelBase(title='title')
        obj.save()
        obj.add_vote("token1", 1)
        obj.add_vote("token2", -1)
        obj.add_vote("token3", 1)

        # vote_total should return an integer
        obj = ModelBase.objects.get(id=obj.id)
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

        # Is_permitted should be True for otherwise published objects in
        # the staging state for instances that define settings.STAGING = True.
        settings.STAGING = False
        self.failIf(staging_obj.is_permitted)
        settings.STAGING = True
        self.failUnless(staging_obj.is_permitted)

        # Is_permitted should be True only if the object is
        # published for the current site.
        published_obj_web = ModelBase(state='published')
        published_obj_web.save()
        published_obj_web.sites.add(web_site)
        published_obj_web.save()
        self.failUnless(published_obj_web.is_permitted)

        # Is_permitted should be False if the object is
        # not published for the current site.
        mobile_site = Site(domain="mobi.address.com")
        mobile_site.save()
        published_obj_mobile = ModelBase(state='published')
        published_obj_mobile.save()
        published_obj_mobile.sites.add(mobile_site)
        published_obj_mobile.save()
        self.failIf(published_obj_mobile.is_permitted)

    def test_can_vote(self):
        # create dummy request object
        request = type('Request', (object,), {})

        class User():
            def is_authenticated(self):
                return False
        request.user = User()
        request.secretballot_token = 'test_token'

        # return false when liking is closed
        obj = ModelBase(
            likes_enabled=True,
            likes_closed=True,
            anonymous_likes=True
        )
        obj.save()
        self.failIf(obj.can_vote(request)[0])

        # return false when liking is disabled
        obj = ModelBase(
            likes_enabled=False,
            likes_closed=False,
            anonymous_likes=True
        )
        obj.save()
        self.failIf(obj.can_vote(request)[0])

        # return false if anonymous and anonymous liking is disabled
        obj = ModelBase(
            likes_enabled=True,
            likes_closed=False,
            anonymous_likes=False
        )
        obj.save()
        self.failIf(obj.can_vote(request)[0])

        # return true if anonymous and anonymous liking is enabled
        obj = ModelBase(
            likes_enabled=True,
            likes_closed=False,
            anonymous_likes=True
        )
        obj.save()
        self.failUnless(obj.can_vote(request))

        # return false if vote already exist
        content_type = ContentType.objects.get(
            app_label="jmbo",
            model="modelbase"
        )
        Vote.objects.create(
            object_id=obj.id,
            token='test_token',
            content_type=content_type, vote=1
        )
        self.failIf(obj.can_vote(request)[0])

    def test_comment_count(self):
        comment_model = comments.get_model()

        # Return 0 if no comments exist.
        obj = ModelBase()
        obj.save()
        self.failUnless(obj.comment_count == 0)

        # Return the number of comments if comments exist. Here it
        # should be 1 since we've created 1 comment.
        comment_obj = comment_model(content_object=obj, site_id=1)
        comment_obj.save()
        obj = ModelBase.objects.get(id=obj.id)
        self.failUnless(obj.comment_count == 1)

        # Return 0 if no comments exist.
        dummy_obj = DummyModel()
        dummy_obj.save()
        dummy_obj = ModelBase.objects.get(id=dummy_obj.id)
        self.failUnless(dummy_obj.comment_count == 0)

        # Return the number of comments if comments exist on the
        # ModelBase object. Here it should be 1 since we've created 1
        # comment on the ModelBase object.
        comment_obj = comment_model(
            content_object=dummy_obj.modelbase_obj,
            site_id=1
        )
        comment_obj.save()
        dummy_obj = ModelBase.objects.get(id=dummy_obj.id)
        self.failUnless(dummy_obj.modelbase_obj.comment_count == 1)

        # If a comment was made on the ModelBase object it should
        # still count for leaf class objects.
        self.failUnless(dummy_obj.comment_count == 1)

        # Add another comment on dummy object and make sure the count
        # is 2 for both the dummy object and its modelbase object.
        comment_obj = comment_model(content_object=dummy_obj, site_id=1)
        comment_obj.save()
        dummy_obj = ModelBase.objects.get(id=dummy_obj.id)
        self.failUnless(dummy_obj.comment_count == 2)
        self.failUnless(dummy_obj.modelbase_obj.comment_count == 2)

        # There should now only be 3 comment objects.
        self.failUnless(comment_model.objects.all().count() == 3)

    def test_can_comment(self):
        # create dummy request object
        request = type('Request', (object,), {})

        class User():
            def is_authenticated(self):
                return False
        request.user = User()
        request.secretballot_token = 'test_token'

        # return false when commenting is closed
        obj = ModelBase(
            comments_enabled=True,
            comments_closed=True,
            anonymous_comments=True
        )
        obj.save()
        self.failIf(obj.can_comment(request)[0])

        # return false when commenting is disabled
        obj = ModelBase(
            comments_enabled=False,
            comments_closed=False,
            anonymous_comments=True
        )
        obj.save()
        self.failIf(obj.can_comment(request)[0])

        # return false if anonymous and anonymous commenting is disabled
        obj = ModelBase(
            comments_enabled=True,
            comments_closed=False,
            anonymous_comments=False
        )
        obj.save()
        self.failIf(obj.can_comment(request)[0])

        # return true if anonymous and anonymous commenting is enabled
        obj = ModelBase(
            comments_enabled=True,
            comments_closed=False,
            anonymous_comments=True
        )
        obj.save()
        self.failUnless(obj.can_comment(request)[0])

    def test_publishing_timezone_awareness(self):
        obj_naive = ModelBase.objects.create(
            title="Obj1",
            publish_on=datetime.now() - timedelta(hours=1)
        )
        obj_aware = ModelBase.objects.create(
            title="Obj2",
            publish_on=timezone.now() - timedelta(hours=1)
        )
        call_command('jmbo_publish')
        self.assertEqual(ModelBase.objects.get(pk=obj_naive.pk).state, 'published')
        self.assertEqual(ModelBase.objects.get(pk=obj_aware.pk).state, 'published')


class ModelBaseAdminTestCase(unittest.TestCase):
    def setUp(self):
        self.user, self.created = User.objects.get_or_create(
            username='test',
            email='test@test.com'
        )

    def test_field_hookup(self):
        model_admin = ModelBaseAdmin(DummyModel, AdminSite())

        # field additions should be added to first fieldsets' fields
        self.failIf('test_editable_field' not in model_admin.\
                fieldsets[0][1]['fields'])
        self.failIf('test_foreign_field' not in model_admin.\
                fieldsets[0][1]['fields'])
        self.failIf('test_many_field' not in model_admin.\
                fieldsets[0][1]['fields'])

        # non editable field additions should not be added to fieldsets
        self.failIf('test_non_editable_field' in \
                model_admin.fieldsets[0][1]['fields'])

        # non field class members should not be added to fieldsets
        self.failIf('test_member' in model_admin.fieldsets[0][1]['fields'])

    def test_save_model(self):
        # setup mock objects
        admin_obj = ModelBaseAdmin(ModelBase, 1)
        request = RequestFactory()
        request.user = self.user

        # After admin save the object's owner should be the current user.
        obj = ModelBase()
        admin_obj.save_model(request, obj, admin_obj.form, 1)
        self.failUnless(obj.owner == self.user)
        obj.save()

        # TODO: If a different user is specified as
        # owner set that user as owner.


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

        # Staging objects should only be available on instances
        # that define settings.STAGING = True.
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

    def test_publish_retract(self):
        today = datetime.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        p1 = ModelBase(title='title', state='published')
        p1.save()
        p1.sites.add(self.web_site)
        p1.save()
        jmbo_publish.Command().handle()
        queryset = ModelBase.permitted.all()
        self.failUnless(p1 in queryset)

        p2 = ModelBase(title='title', publish_on=today)
        p2.save()
        p2.sites.add(self.web_site)
        p2.save()
        jmbo_publish.Command().handle()
        queryset = ModelBase.permitted.all()
        self.failUnless(p2 in queryset)

        p4 = ModelBase(title='title', publish_on=today, retract_on=tomorrow)
        p4.save()
        p4.sites.add(self.web_site)
        p4.save()
        jmbo_publish.Command().handle()
        queryset = ModelBase.permitted.all()
        self.failUnless(p4 in queryset)

        p5 = ModelBase(title='title', publish_on=tomorrow)
        p5.save()
        p5.sites.add(self.web_site)
        p5.save()
        jmbo_publish.Command().handle()
        queryset = ModelBase.permitted.all()
        self.failIf(p5 in queryset)

        p6 = ModelBase(title='title', publish_on=yesterday, retract_on=today)
        p6.save()
        p6.sites.add(self.web_site)
        p6.save()
        jmbo_publish.Command().handle()
        queryset = ModelBase.permitted.all()
        self.failIf(p6 in queryset)

        p7 = ModelBase(title='title', publish_on=tomorrow, retract_on=tomorrow)
        p7.save()
        p7.sites.add(self.web_site)
        p7.save()
        jmbo_publish.Command().handle()
        queryset = ModelBase.permitted.all()
        self.failIf(p7 in queryset)

        p8 = ModelBase(
            title='title', publish_on=yesterday, retract_on=yesterday
        )
        p8.save()
        p8.sites.add(self.web_site)
        p8.save()
        jmbo_publish.Command().handle()
        queryset = ModelBase.permitted.all()
        self.failIf(p8 in queryset)

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

    def test_related_permitted_query(self):
        # Targets for DummyModel to point to
        dtmb_p = DummyTargetModelBase(title='dtmb_p', state='published')
        dtmb_p.save()
        dtmb_p.sites.add(self.web_site)
        dtmb_p.save()
        dtmb_up = DummyTargetModelBase(title='dtmb_up')
        dtmb_up.save()
        dtmb_up.sites.add(self.web_site)
        dtmb_up.save()

        # Dummy model - published
        dm_p = DummyModel(
            title='title',
            state='published',
            test_foreign_published=dtmb_p,
            test_foreign_unpublished=dtmb_up,
        )
        dm_p.save()
        dm_p.test_many_published.add(dtmb_p)
        dm_p.test_many_unpublished.add(dtmb_up)
        dm_p.save()

        # Dummy model - unpublished
        dm_up = DummyModel(
            title='title',
        )
        dm_up.save()

        # Source models that point at DummyModel
        # Published, points to published DummyModel
        dsmb_p = DummySourceModelBase(
            title='dsmb_p', points_to=dm_p, state='published'
        )
        dsmb_p.save()
        dsmb_p.sites.add(self.web_site)
        dsmb_p.save()

        # Unpublished, points to published DummyModel
        dsmb_up = DummySourceModelBase(
            title='dsmb_up', points_to=dm_p,
        )
        dsmb_up.save()
        dsmb_up.sites.add(self.web_site)
        dsmb_up.save()

        # Published, points to unpublished DummyModel
        dsmb_p2 = DummySourceModelBase(
            title='dsmb_p2', points_to=dm_up, state='published'
        )
        dsmb_p2.save()
        dsmb_p2.sites.add(self.web_site)
        dsmb_p2.save()


class InclusionTagsTestCase(unittest.TestCase):
    def setUp(self):
        obj = TestModel(title='title', state='published')
        obj.save()
        self.context = template.Context({'object': obj})

    def test_render_tag(self):
        # load correct template for provided object and type
        t = Template("{% load jmbo_inclusion_tags %}\
{% render_object object 'test_block' %}")
        result = t.render(self.context)
        expected_result = u'Test string for testing purposes\n'
        self.failUnlessEqual(result, expected_result)

        # If template is not available for object
        # fall back to default content template.
        obj = BranchModel(title='title', state='published')
        obj.save()
        self.context = template.Context({'object': obj})
        t = Template("{% load jmbo_inclusion_tags %}\
{% render_object object 'test_block' %}")
        result = t.render(self.context)
        self.failUnless(result)

        # Return the empty string if no template can be found for the given
        # type for either obj or content.
        t = Template("{% load jmbo_inclusion_tags %}\
{% render_object object 'foobar' %}")
        result = t.render(self.context)
        expected_result = u''
        self.failUnlessEqual(result, expected_result)


class TemplateTagsTestCase(unittest.TestCase):
    def setUp(self):

        def url_callable(obj):
            return 'Test URL method using object %s' % obj.__class__.__name__

        class CallableURL(object):

            def __call__(self):
                return url_callable

        obj = TestModel(title='title', state='published')
        obj.save()
        self.context = template.Context({
            'object': obj,
            'url_callable': CallableURL(),
        })

    @classmethod
    def setUpClass(cls):
        # Add an extra site
        site, dc = Site.objects.get_or_create(name='another', domain='another.com')

    def test_jmbocache(self):
        # Caching on same site
        t = Template("{% load jmbo_template_tags %}\
            {% jmbocache 1200 'test_jmbocache' %}1{% endjmbocache %}"
        )
        result1 = t.render(self.context)
        t = Template("{% load jmbo_template_tags %}\
            {% jmbocache 1200 'test_jmbocache' %}2{% endjmbocache %}"
        )
        result2 = t.render(self.context)
        self.failUnlessEqual(result1, result2)

        # Caching on different sites
        t = Template("{% load jmbo_template_tags %}\
            {% jmbocache 1200 'test_jmbocache' %}1{% endjmbocache %}"
        )
        result1 = t.render(self.context)
        settings.SITE_ID = 2
        Site.objects.clear_cache()
        t = Template("{% load jmbo_template_tags %}\
            {% jmbocache 1200 'test_jmbocache' %}2{% endjmbocache %}"
        )
        result2 = t.render(self.context)
        settings.SITE_ID = 2
        Site.objects.clear_cache()
        self.failIfEqual(result1, result2)

        # Check that undefined variables do not break caching
        t = Template("{% load jmbo_template_tags %}\
            {% jmbocache 1200 'test_jmbocache_undefined' aaa %}1{% endjmbocache %}"
        )
        result1 = t.render(self.context)
        t = Template("{% load jmbo_template_tags %}\
            {% jmbocache 1200 'test_jmbocache_undefined' bbb %}2{% endjmbocache %}"
        )
        result2 = t.render(self.context)
        self.failUnlessEqual(result1, result2)

        # Check that translation proxies are valid variables
        t = Template("{% load jmbo_template_tags %}\
            {% jmbocache 1200 'test_jmbocache_xlt' _('aaa') %}1{% endjmbocache %}"
        )
        result1 = t.render(self.context)
        t = Template("{% load jmbo_template_tags %}\
            {% jmbocache 1200 'test_jmbocache_xlt' _('aaa') %}2{% endjmbocache %}"
        )
        result2 = t.render(self.context)
        self.failUnlessEqual(result1, result2)

        # Check that large integer variables do not break caching
        t = Template("{% load jmbo_template_tags %}\
            {% jmbocache 1200 'test_jmbocache_large' 565417614189797377 %}1{% endjmbocache %}"
        )
        result1 = t.render(self.context)
        t = Template("{% load jmbo_template_tags %}\
            {% jmbocache 1200 'test_jmbocache_large' 565417614189797377 %}2{% endjmbocache %}"
        )
        result2 = t.render(self.context)
        self.failUnlessEqual(result1, result2)


class ViewsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.request = RequestFactory()
        cls.client = Client()

        cls.obj = ModelBase.objects.create(title="title1", state="published")
        cls.obj.sites = Site.objects.all()
        cls.obj.save()

    def test_detail_view(self):
        response = self.client.get(self.obj.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_detail_view(self):
        url = reverse("object_list", args=["jmbo", "modelbase"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.failUnless("""<div class="jmbo-view-modifier">""" in response.content)


if USE_GIS:
    class LocationAwarenessTestCase(unittest.TestCase):
        def setUp(self):
            country = Country(name="South Africa", country_code="ZA")
            country.save()
            self.ct = City(
                name="Cape Town",
                country=country,
                coordinates=fromstr('POINT(18.423218 -33.925839)', srid=4326)
            )
            self.ct.save()
            loc1 = Location(
                city=self.ct,
                country=country,
                coordinates=fromstr('POINT(18.41 -33.91)', srid=4326),
                name='loc1'
            )
            loc1.save()
            self.model = ModelBase(title="title1", location=loc1)
            self.model.save()

        def test_distance_calculation(self):
            qs = ModelBase.objects.distance(self.ct.coordinates)
            for obj in qs:
                if obj.distance is not None:
                    self.assertEqual(obj.location.coordinates.distance(self.ct.coordinates), obj.distance)
