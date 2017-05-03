import os
from shutil import rmtree

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.core.files.base import ContentFile
from django.db import transaction, IntegrityError
from django.test import TestCase, override_settings
from django.utils import timezone

from category.models import Category
import django_comments
from photologue.models import PhotoSize, PhotoSizeCache
from secretballot.models import Vote

from jmbo.models import ModelBase, Relation, Image, ModelBaseImage, ImageOverride
from jmbo.tests.models import DummyRelationalModel1, DummyRelationalModel2, \
    DummyTargetModelBase, DummySourceModelBase, DummyModel, TrunkModel, \
    BranchModel, LeafModel, TestModel
from jmbo.tests.extra.models import LeafModel as ExtraLeafModel


RES_DIR = os.path.join(os.path.dirname(__file__), "res")
IMAGE_PATH = os.path.join(RES_DIR, "image.jpg")
IMAGE_OVERRIDE_PATH = os.path.join(RES_DIR, "override.jpg")


def set_image(obj):
    image = Image.objects.create(title=IMAGE_PATH)
    image.image.save(
        os.path.basename(IMAGE_PATH),
        ContentFile(open(IMAGE_PATH, "rb").read())
    )
    ModelBaseImage.objects.create(modelbase=obj, image=image)


def set_image_override(image):
    override = ImageOverride.objects.create(
        image=image,
        photo_size=PhotoSize.objects.get(name="thumbnail")
    )
    override.replacement.save(
        os.path.basename(IMAGE_OVERRIDE_PATH),
        ContentFile(open(IMAGE_OVERRIDE_PATH, "rb").read())
    )


class ModelBaseTestCase(TestCase):
    fixtures = ["sites.json"]

    @classmethod
    def setUpTestData(cls):
        super(ModelBaseTestCase, cls).setUpTestData()
        cls.web_site = Site.objects.all().first()
        cls.mobile_site = Site.objects.all().last()
        call_command("load_photosizes")
        PhotoSizeCache().reset()

        # Clear media root
        rmtree(settings.MEDIA_ROOT)

    def test_save(self):
        before_save = timezone.now()

        # created field should be set on save
        obj = ModelBase(title="title")
        obj.save()

        # created field should be set to current datetime on save
        after_save = timezone.now()
        self.failIf(obj.created > after_save or obj.created < before_save)

        # If a user supplies a created date use that
        # instead of the current datetime.
        test_datetime = timezone.make_aware(timezone.datetime(2008, 10, 10, 12, 12))
        obj = ModelBase(title="title", created=test_datetime)
        obj.save()
        self.failIf(obj.created != test_datetime)

        # modified should be set to current datetime on each save
        before_save = timezone.now()
        obj = ModelBase(title="title")
        obj.save()
        after_save = timezone.now()
        self.failIf(obj.modified > after_save or obj.modified < before_save)

        # leaf class content type should be set on save
        obj = DummyModel(title="title")
        obj.save()
        self.failUnless(obj.content_type == ContentType.objects.\
                get_for_model(DummyModel))

        # leaf class class name should be set on save
        self.failUnless(obj.class_name == DummyModel.__name__)

        # Correct leaf class content type should be retained
        # over base class" content type.
        base = obj.modelbase_ptr
        base.save()
        self.failUnless(
            base.content_type == ContentType.objects.get_for_model(DummyModel)
        )

        # Correct leaf class class name should be
        # retained over base class" class name.
        self.failUnless(base.class_name == DummyModel.__name__)

    def test_unique_slugs(self):
        obj_1 = ModelBase(title="object for site 1")
        obj_1.save()
        obj_1.sites.add(self.web_site)
        obj_1.slug = "generic_slug"
        obj_1.save()

        # Create an object for site 2
        obj_2 = ModelBase(title="object for site 2")
        obj_2.save()
        obj_2.sites.add(self.mobile_site)
        obj_2.slug = "generic_slug"
        obj_2.save()

        # Trying to add site_1 should raise an error.
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                obj_2.sites.add(self.web_site)
                obj_2.save()

        # When the slugs differ, you can add site_1.
        obj_2.slug = "generic_slug_2"
        obj_2.sites.add(self.web_site)
        obj_2.save()

        # Trying to change the slug to an existing one should raise an error.
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                obj_2.slug = "generic_slug"
                obj_2.save()

    def test_as_leaf_class(self):
        leaf = LeafModel(title="title")
        leaf.save()
        extra_leaf = ExtraLeafModel(title="title")
        extra_leaf.save()

        # Always return the leaf class, no matter where we are in the hierarchy
        self.failUnless(TrunkModel.objects.get(slug=leaf.slug).\
                as_leaf_class() == leaf)
        self.failUnless(BranchModel.objects.get(slug=leaf.slug).\
                as_leaf_class() == leaf)
        self.failUnless(LeafModel.objects.get(slug=leaf.slug).\
                as_leaf_class() == leaf)
        self.failUnless(ModelBase.objects.get(slug=extra_leaf.slug).\
                as_leaf_class() == extra_leaf)

    def test_vote_total(self):
        # create object with some votes
        obj = ModelBase(title="title")
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
        # create unpublished item
        unpublished_obj = ModelBase(title="title", state="unpublished")
        unpublished_obj.save()
        unpublished_obj.sites.add(self.web_site)
        unpublished_obj.save()

        # create published item
        published_obj = ModelBase(title="title", state="published")
        published_obj.save()
        published_obj.sites.add(self.web_site)
        published_obj.save()

        # is_permitted should be False for unpublished objects
        self.failIf(unpublished_obj.is_permitted)

        # is_permitted should be True for published objects
        self.failUnless(published_obj.is_permitted)

        # Is_permitted should be True only if the object is
        # published for the current site.
        published_obj_web = ModelBase(state="published")
        published_obj_web.save()
        published_obj_web.sites.add(self.web_site)
        published_obj_web.save()
        self.failUnless(published_obj_web.is_permitted)

        # Is_permitted should be False if the object is
        # not published for the current site.
        published_obj_mobile = ModelBase(state="published")
        published_obj_mobile.save()
        published_obj_mobile.sites.add(self.mobile_site)
        published_obj_mobile.save()
        self.failIf(published_obj_mobile.is_permitted)

    def test_can_vote(self):
        # create dummy request object
        request = type("Request", (object,), {})

        class User():
            def is_authenticated(self):
                return False
        request.user = User()
        request.secretballot_token = "test_token"

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
            token="test_token",
            content_type=content_type, vote=1
        )
        self.failIf(obj.can_vote(request)[0])

    def test_comment_count(self):
        comment_model = django_comments.get_model()

        # Return 0 if no comments exist.
        obj = ModelBase()
        obj.save()
        self.failUnless(obj.comment_count == 0)

        # Return the number of comments if comments exist. Here it
        # should be 1 since we"ve created 1 comment.
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
        # ModelBase object. Here it should be 1 since we"ve created 1
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
        request = type("Request", (object,), {})

        class User():
            def is_authenticated(self):
                return False
        request.user = User()
        request.secretballot_token = "test_token"

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

    @override_settings(USE_TZ=False)
    def test_publishing_timezone_unaware(self):
        obj_naive = ModelBase.objects.create(
            title="Obj1",
            publish_on=timezone.datetime.now() - timezone.timedelta(hours=1)
        )
        call_command("jmbo_publish")
        self.assertEqual(ModelBase.objects.get(pk=obj_naive.pk).state, "published")

    def test_publishing_timezone_aware(self):
        obj_aware = ModelBase.objects.create(
            title="Obj2",
            publish_on=timezone.now() - timezone.timedelta(hours=1)
        )
        call_command("jmbo_publish")
        self.assertEqual(ModelBase.objects.get(pk=obj_aware.pk).state, "published")

    def test_unicode(self):
        obj = TestModel(title="Title")
        obj.save()
        obj.sites = Site.objects.all()
        obj.publish()
        self.assertEqual(unicode(obj), u"Title (all sites)")
        obj = TestModel(title="Title")
        obj.save()
        obj.sites = [1]
        obj.publish()
        self.assertEqual(unicode(obj), u"Title (testserver)")

    def test_get_absolute_url(self):
        leaf = LeafModel.objects.create(title="title")
        extra_leaf = ExtraLeafModel.objects.create(title="title")
        # Leaf declares a url pattern
        self.assertEqual(
            leaf.get_absolute_url(),
            "/tests/detail/%s/" % leaf.slug
        )
        # Extra Leaf does not declare a url pattern
        self.assertEqual(
            extra_leaf.get_absolute_url(),
            "/jmbo/detail/%s/" % extra_leaf.slug
        )

    def test_get_absolute_url_categorized(self):
        category = Category.objects.create(title="cat1", slug="cat1")
        leaf = LeafModel.objects.create(
            title="title", primary_category=category
        )
        extra_leaf = ExtraLeafModel.objects.create(
            title="title", primary_category=category
        )
        # Leaf declares a url pattern
        self.assertEqual(
            leaf.get_absolute_url_categorized(),
            "/tests/detail/%s/%s/" % (category.slug, leaf.slug)
        )
        # Extra Leaf does not declare a url pattern
        self.assertEqual(
            extra_leaf.get_absolute_url_categorized(),
            "/jmbo/detail/%s/%s/" % (category.slug, extra_leaf.slug)
        )

    def test_get_related_items(self):
        obj1 = ModelBase.objects.create(title="obj1")
        obj2 = ModelBase.objects.create(title="obj2")
        obj3 = ModelBase.objects.create(title="obj2")
        Relation.objects.create(
            source=obj1, target=obj2, name="obj-objs"
        )
        Relation.objects.create(
            source=obj3, target=obj1, name="multi"
        )
        self.assertEqual(obj1.get_related_items()[0].id, obj2.id)
        self.assertEqual(obj1.get_related_items(name="obj-objs")[0].id, obj2.id)
        self.assertEqual(len(obj1.get_related_items(name="---")), 0)
        self.assertEqual(obj2.get_related_items(direction="reverse")[0].id, obj1.id)
        self.assertEqual(len(obj1.get_related_items(direction="both")), 2)

    def test_get_permitted_related_items(self):
        obj1 = ModelBase.objects.create(title="obj1")
        obj1.sites = Site.objects.all()
        obj1.publish()
        obj2 = ModelBase.objects.create(title="obj2")
        obj2.sites = Site.objects.all()
        obj2.publish()
        obj3 = ModelBase.objects.create(title="obj3")
        Relation.objects.create(
            source=obj1, target=obj2, name="obj-objs"
        )
        Relation.objects.create(
            source=obj1, target=obj3, name="obj-objs"
        )
        self.assertEqual(obj1.get_permitted_related_items()[0].id, obj2.id)
        self.failIf(obj3 in obj1.get_permitted_related_items())

    def test_image_detail_url(self):
        leaf = LeafModel.objects.create(title="title")
        set_image(leaf)
        extra_leaf = ExtraLeafModel.objects.create(title="title")
        set_image(extra_leaf)

        # Leaf gets image from BranchModel
        self.assertTrue(
            leaf.image_detail_url.startswith("photologue/photos/cache/image_")
        )
        self.assertTrue(
            leaf.image_detail_url.endswith("_tests_branchmodel_detail.jpg")
        )

        # Extra Leaf gets image from ModelBase
        self.assertTrue(
            extra_leaf.image_detail_url.startswith(
                "photologue/photos/cache/image_"
            )
        )
        self.assertTrue(
            extra_leaf.image_detail_url.endswith("_jmbo_modelbase_detail.jpg")
        )

    def test_image_list_url(self):
        leaf = LeafModel.objects.create(title="title")
        set_image(leaf)
        extra_leaf = ExtraLeafModel.objects.create(title="title")
        set_image(extra_leaf)

        # Leaf gets image from BranchModel
        self.assertTrue(
            leaf.image_list_url.startswith("photologue/photos/cache/image_")
        )
        self.assertTrue(
            leaf.image_list_url.endswith("_tests_branchmodel_list.jpg")
        )

        # Extra Leaf gets image from ModelBase
        self.assertTrue(
            extra_leaf.image_list_url.startswith(
                "photologue/photos/cache/image_"
            )
        )
        self.assertTrue(
            extra_leaf.image_list_url.endswith("_jmbo_modelbase_list.jpg")
        )

    def test_image_override_url(self):
        leaf = LeafModel.objects.create(title="title")
        set_image(leaf)
        set_image_override(leaf.image)
        self.assertTrue(
            leaf.image.get_thumbnail_url().endswith("override.jpg")
        )
