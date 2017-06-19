import types

from django.db import models, IntegrityError
from django.db.models import signals, Sum
from django.core.cache import cache
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site, SiteManager
from django.utils.encoding import smart_unicode
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, ugettext
from django.conf import settings

from crum import get_current_request
import django_comments
from layers.models import Layer
from photologue.models import ImageModel, PhotoSize, get_storage_path
from preferences import Preferences
import secretballot
from secretballot.models import Vote
from sortedm2m.fields import SortedManyToManyField

from jmbo.managers import PermittedManager, DefaultManager
from jmbo.utils import generate_slug
import jmbo.signals
from jmbo import USE_GIS
from jmbo import monkey


class JmboPreferences(Preferences):
    __module__ = "preferences.models"


class Image(ImageModel):
    title = models.CharField(
        _("Title"),
        max_length=200,
        db_index=True,
        help_text=_("A short descriptive title."),
    )
    subtitle = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        default="",
        help_text=_("Some titles may be the same and cause confusion in admin \
UI. A subtitle makes a distinction."),
    )
    attribution = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        help_text=_("Attribution for the image, eg. Shutterstock.")
    )

    class Meta:
        ordering = ("title",)

    def __unicode__(self):
        if self.subtitle:
            return "%s - %s" % (self.title, self.subtitle)
        return self.title

    def _get_SIZE_url(self, size):
        override = self.imageoverride_set.filter(photo_size__name=size).first()
        if override is not None:
            return override.replacement.url
        return super(Image, self)._get_SIZE_url(size)


class ImageOverride(models.Model):
    """Allows manual setting of a photo size for an image"""
    replacement = models.ImageField(upload_to=get_storage_path)
    image = models.ForeignKey(Image)
    photo_size = models.ForeignKey(PhotoSize)

    class Meta:
        unique_together = ("image", "photo_size")


class ModelBase(models.Model):
    objects = DefaultManager()
    permitted = PermittedManager()

    state = models.CharField(
        max_length=32,
        choices=(
            ("unpublished", "Unpublished"),
            ("published", "Published"),
        ),
        default="unpublished",
        editable=False,
        db_index=True,
        blank=True,
        null=True,
    )
    publish_on = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        help_text=_("""Date and time on which to publish this item (the state \
will change to "published")."""),
    )
    retract_on = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        help_text=_("""Date and time on which to retract this item (the state \
will change to "unpublished")."""),
    )
    slug = models.SlugField(
        max_length=255,
        db_index=True,
    )
    title = models.CharField(
        _("Title"),
        max_length=200,
        db_index=True,
        help_text=_("A short descriptive title."),
    )
    subtitle = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        default="",
        help_text=_("Some titles may be the same and cause confusion in admin \
UI. A subtitle makes a distinction."),
    )
    description = models.TextField(
        help_text=_("A short description. More verbose than the title but \
limited to one or two sentences. It may not contain any markup."),
        blank=True,
        null=True
    )
    created = models.DateTimeField(
        _("Created Date & Time"),
        blank=True,
        db_index=True,
        help_text=_("Date and time on which this item was created. This is \
automatically set on creation but can be changed subsequently.")
    )
    modified = models.DateTimeField(
        _("Modified Date & Time"),
        db_index=True,
        editable=False,
        help_text=_("Date and time on which this item was last modified. This \
is automatically set each time the item is saved.")
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
    )
    owner_override = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        help_text=_("If the author is not a registered user then set it here, \
eg. Reuters.")
    )
    content_type = models.ForeignKey(
        ContentType,
        editable=False,
        null=True
    )
    class_name = models.CharField(
        max_length=32,
        editable=False,
        null=True
    )
    categories = models.ManyToManyField(
        "category.Category",
        blank=True,
        null=True,
        help_text=_("Categorize this item.")
    )
    primary_category = models.ForeignKey(
        "category.Category",
        blank=True,
        null=True,
        help_text=_("Primary category for this item. Used to determine the \
            object's absolute / default URL."),
        related_name="primary_modelbase_set",
    )
    tags = models.ManyToManyField(
        "category.Tag",
        blank=True,
        null=True,
        help_text=_("Tag this item.")
    )
    sites = models.ManyToManyField(
        "sites.Site",
        blank=True,
        null=True,
        help_text=_("Makes item eligible to be published on selected sites."),
    )
    layers = models.ManyToManyField(
        Layer,
        blank=True,
        null=True,
        help_text=_("Makes item eligible to be published on selected layers."),
    )
    comments_enabled = models.BooleanField(
        verbose_name=_("Commenting enabled"),
        help_text=_("Enable commenting for this item. Comments will not \
display when disabled."),
        default=True,
    )
    anonymous_comments = models.BooleanField(
        verbose_name=_("Anonymous Commenting Enabled"),
        help_text=_("Enable anonymous commenting for this item."),
        default=True,
    )
    comments_closed = models.BooleanField(
        verbose_name=_("Commenting Closed"),
        help_text=_("Close commenting for this item. Comments will still \
display, but users won't be able to add new comments."),
        default=False,
    )
    likes_enabled = models.BooleanField(
        verbose_name=_("Liking Enabled"),
        help_text=_("Enable liking for this item. Likes will not display \
when disabled."),
        default=True,
    )
    anonymous_likes = models.BooleanField(
        verbose_name=_("Anonymous Liking Enabled"),
        help_text=_("Enable anonymous liking for this item."),
        default=True,
    )
    likes_closed = models.BooleanField(
        verbose_name=_("Liking Closed"),
        help_text=_("Close liking for this item. Likes will still display, \
but users won't be able to add new likes."),
        default=False,
    )
    if USE_GIS:
        from atlas.models import Location
        location = models.ForeignKey(
            Location,
            blank=True,
            null=True,
            help_text=_("A location that can be used for content filtering."),
        )
    comment_count = models.PositiveIntegerField(default=0, editable=False)
    vote_total = models.PositiveIntegerField(default=0, editable=False)
    images = SortedManyToManyField(
        Image,
        null=True,
        blank=True,
        sort_value_field_name="position",
        through="ModelBaseImage"
    )

    class Meta:
        ordering = ("-publish_on", "-created")

    def as_leaf_class(self):
        """Returns the leaf class no matter where the calling instance is in
        the inheritance hierarchy. Inspired by
        http://www.djangosnippets.org/snippets/1031/
        """
        try:
            instance = self.__getattribute__(self.class_name.lower())
        except (AttributeError, self.DoesNotExist):
            content_type = self.content_type
            model = content_type.model_class()
            if (model == ModelBase):
                return self
            instance = model.objects.get(id=self.id)

        # If distance was dynamically added to this object it needs to be
        # added to the leaf object as well.
        if hasattr(self, "distance"):
            instance.distance = self.distance

        return instance

    def get_absolute_url(self, category=None):
        # Reverse by traversing upwards over inheritance hierarchy and
        # following naming convention. Try namespace first, then fall back to
        # verbose view naming convention.
        ct = self.content_type
        kls = ct.model_class()
        while ct.model != "model":
            try:
                if category is None:
                    return reverse(
                        "%s:%s-detail" % \
                            (ct.app_label, ct.model), args=[self.slug]
                    )
                else:
                    return reverse(
                        "%s:%s-categorized-detail" % \
                            (ct.app_label, ct.model), args=[category.slug, self.slug]
                    )
            except NoReverseMatch:
                pass
            try:
                if category is None:
                    return reverse(
                        "%s-%s-detail" % \
                            (ct.app_label, ct.model), args=[self.slug]
                    )
                else:
                    return reverse(
                        "%s-%s-categorized-detail" % \
                            (ct.app_label, ct.model), args=[category.slug, self.slug]
                    )
            except NoReverseMatch:
                kls = kls.__bases__[0]
                if kls == models.Model:
                    break
                ct = ContentType.objects.get_for_model(kls)

        if category is None:
            return reverse("jmbo:modelbase-detail", args=[self.slug])
        else:
            return reverse(
                "jmbo:modelbase-categorized-detail",
                args=[category.slug, self.slug]
            )

    def get_absolute_url_categorized(self):
        """Absolute url with category incorporated into the url. The normal
        template when navigating to get_absolute_url is still rendered. Hint:
        SEO."""

        category = None
        if self.primary_category:
            category = self.primary_category
        else:
            categories = self.categories.all()
            # Small list so no need for exists method
            if categories:
                category = categories[0]

        return self.get_absolute_url(category)

    def save(self, *args, **kwargs):
        now = timezone.now()

        # Set created time to now if not already set
        if not self.created:
            self.created = now

        # Set modified to now on each save
        set_modified = kwargs.pop("set_modified", True)
        if set_modified:
            self.modified = now

        # Set leaf class content type
        if not self.content_type:
            self.content_type = ContentType.objects.get_for_model(\
                    self.__class__)

        # Set leaf class class name
        if not self.class_name:
            self.class_name = self.__class__.__name__

        # Set title as slug uniquely exactly once
        if not self.slug:
            self.slug = generate_slug(self, self.title)

        # Raise an error if the slug is not unique per site.
        if self.id:
            for site in self.sites.all():
                q = jmbo.models.ModelBase.objects.filter(
                        slug=self.slug, sites=site).exclude(id=self.id)
                if q.exists():
                    raise IntegrityError(
                        "The slug %s is already in use for site %s by %s" %
                        (self.slug, site.domain, q[0].title))

        super(ModelBase, self).save(*args, **kwargs)

    def __unicode__(self):
        # This method gets called repeatedly in admin so cache
        key = "jmbo-mb-uc-%s-%s" % \
            (self.pk, self.modified and int(self.modified.strftime("%s")) or 0)
        cached = cache.get(key, None)
        if cached is not None:
            return cached

        # Append site(s) information intelligently
        suffix = ""
        sites = self.sites.all()
        if not sites:
            suffix = " (%s)" % ugettext("no sites")
        else:
            all_sites = Site.objects.all()
            len_all_sites = len(all_sites)
            if len_all_sites > 1:
                if len(sites) == len_all_sites:
                    suffix = " (%s)" % ugettext("all sites")
                else:
                    suffix = " (%s)" % ", ".join([s.name for s in sites])
        if self.subtitle:
            result = "%s - %s%s" % (self.title, self.subtitle, suffix)
        else:
            result = "%s%s" % (self.title, suffix)
        cache.set(key, result, 300)
        return result

    @property
    def is_permitted(self):
        if self.state == "unpublished":
            return False
        elif self.state == "published":
            site = get_current_site(get_current_request())
            return self.sites.filter(id__exact=site.id).exists()

        return False

    @property
    def modelbase_obj(self):
        if self.__class__ == ModelBase:
            return self
        else:
            """
            Use self._meta.get_ancestor_link instead of self.modelbase_ptr since
            the name of the link could be different
            """
            link_name = self._meta.get_ancestor_link(ModelBase).name
            return getattr(self, link_name)

    def can_vote(self, request):
        """
        Determines whether or not the current user can vote.
        Returns a bool as well as a string indicating the current vote status,
        with vote status being one of: "closed", "disabled",
        "auth_required", "can_vote", "voted"
        """
        modelbase_obj = self.modelbase_obj

        # Can't vote if liking is closed
        if modelbase_obj.likes_closed:
            return False, "closed"

        # Can't vote if liking is disabled
        if not modelbase_obj.likes_enabled:
            return False, "disabled"

        # Anonymous users can't vote if anonymous likes are disabled
        if not request.user.is_authenticated() and not \
                modelbase_obj.anonymous_likes:
            return False, "auth_required"

        # Return false if existing votes are found
        if Vote.objects.filter(
            object_id=modelbase_obj.id,
            token=request.secretballot_token
        ).count() == 0:
            return True, "can_vote"
        else:
            return False, "voted"

    def can_comment(self, request):
        modelbase_obj = self.modelbase_obj

        # Can't comment if commenting is closed
        if modelbase_obj.comments_closed:
            return False, "closed"

        # Can't comment if commenting is disabled
        if not modelbase_obj.comments_enabled:
            return False, "disabled"

        # Anonymous users can't comment if anonymous comments are disabled
        if not request.user.is_authenticated() and not \
                modelbase_obj.anonymous_comments:
            return False, "auth_required"

        return True, "can_comment"

    @property
    def _vote_total(self):
        """
        Calculates vote total (+1 for upvote and -1 for downvote). We are
        adding a method here instead of relying on django-secretballot"s
        addition since that doesn't work for subclasses.
        """
        votes = Vote.objects.filter(object_id= \
            self.id).aggregate(Sum("vote"))["vote__sum"]
        return votes if votes else 0

    @property
    def _comment_count(self):
        """
        Counts total number of comments on ModelBase object.
        Comments should always be recorded on ModelBase objects.
        """
        # Get the comment model.
        comment_model = django_comments.get_model()

        modelbase_content_type = ContentType.objects.get(
            app_label="jmbo",
            model="modelbase"
        )

        # Create a qs filtered for the ModelBase or content_type objects.
        qs = comment_model.objects.filter(
            content_type__in=[self.content_type, modelbase_content_type],
            object_pk=smart_unicode(self.pk),
        )

        # The is_public and is_removed fields are implementation details of the
        # built-in comment model"s spam filtering system, so they might not
        # be present on a custom comment model subclass. If they exist, we
        # should filter on them.
        try:
            comment_model._meta.get_field("is_public")
            is_public = True
        except models.FieldDoesNotExist:
            is_public = False
        if is_public:
            qs = qs.filter(is_public=True)

        if getattr(settings, "COMMENTS_HIDE_REMOVED", True):
            try:
                comment_model._meta.get_field("is_removed")
                is_removed = True
            except models.FieldDoesNotExist:
                is_removed = False
            if is_removed:
                qs = qs.filter(is_removed=False)

        # Return amount of items in qs
        return qs.count()

    @property
    def image(self):
        return self.images.all().first()

    def _get_image_url(self, type="detail"):
        """If a photosize is defined for the content type return the
        corresponding image URL, else traverse upwards over inheritance
        hierarchy until a URL is found.  This allows content types which may
        typically have images which are not landscaped (eg human faces) to
        define their own sizes."""

        image = self.image
        if not image:
            return None

        ct = self.content_type
        kls = ct.model_class()
        while ct.model != "model":
            method = "get_%s_%s_%s_url" % (ct.app_label, ct.model, type)
            if hasattr(image, method):
                return getattr(image, method)()
            else:
                kls = kls.__bases__[0]
                if kls == models.Model:
                    break
                ct = ContentType.objects.get_for_model(kls)

        return getattr(image, "get_jmbo_modelbase_%s_url" % type)()

    @property
    def image_detail_url(self):
        return self._get_image_url("detail")

    @property
    def image_list_url(self):
        return self._get_image_url("list")

    def get_related_items(self, name=None, direction="forward", permitted=False):
        """If direction is forward get items self points to by name name. If
        direction is reverse get items pointing to self to by name name.

        There is no logical value in having a large amount of relations on
        an object. This nature of the data makes the use of the ids iterators
        safe.
        """

        if permitted:
            manager = ModelBase.permitted
        else:
            manager = ModelBase.objects

        if direction == "both":
            ids = Relation.objects.filter(
                source_content_type=self.content_type,
                source_object_id=self.id
            )
            if name:
                ids = ids.filter(name=name)
            ids_forward = ids.values_list("target_object_id", flat=True)

            ids = Relation.objects.filter(
                target_content_type=self.content_type,
                target_object_id=self.id
            )
            if name:
                ids = ids.filter(name=name)
            ids_reverse = ids.values_list("source_object_id", flat=True)

            ids = [i for i in ids_forward] + [i for i in ids_reverse]
            return manager.filter(id__in=ids).order_by("-publish_on", "-created")

        elif direction == "forward":
            ids = Relation.objects.filter(
                source_content_type=self.content_type,
                source_object_id=self.id
            )
            if name:
                ids = ids.filter(name=name)
            ids = ids.values_list("target_object_id", flat=True)
            return manager.filter(id__in=ids).order_by("-publish_on", "-created")

        elif direction == "reverse":
            ids = Relation.objects.filter(
                target_content_type=self.content_type,
                target_object_id=self.id
            )
            if name:
                ids = ids.filter(name=name)
            ids = ids.values_list("source_object_id", flat=True)
            return manager.filter(id__in=ids).order_by("-publish_on", "-created")

        else:
            return manager.none()

    def get_permitted_related_items(self, name=None, direction="forward"):
        return self.get_related_items(name, direction, True)

    def natural_key(self):
        return (self.slug,)

    def publish(self):
        if self.state != "published":
            now = timezone.now()
            self.state = "published"
            self.publish_on = now
            if self.retract_on and (self.retract_on <= now):
                self.retract_on = None
            self.save()

    def unpublish(self):
        if self.state != "unpublished":
            self.state = "unpublished"
            self.retract_on = timezone.now()
            self.save()


class ModelBaseImage(models.Model):
    modelbase = models.ForeignKey(ModelBase)
    image = models.ForeignKey(Image, related_name="image_link_to_modelbase")
    position = models.PositiveIntegerField(default=0)
    _sort_field_name = "position"

    class Meta:
        ordering = ("position",)


class Relation(models.Model):
    """Generic relation between two objects"""
    source_content_type = models.ForeignKey(
        ContentType,
        related_name="relation_source_content_type",
    )
    source_object_id = models.PositiveIntegerField()
    source = GenericForeignKey(
        "source_content_type", "source_object_id"
    )
    target_content_type = models.ForeignKey(
        ContentType,
        related_name="relation_target_content_type",
    )
    target_object_id = models.PositiveIntegerField()
    target = GenericForeignKey(
        "target_content_type", "target_object_id"
    )
    name = models.CharField(
        max_length=32,
        db_index=True,
        help_text="A name used to identify the relation. It must follow the \
naming convention a-underscore-b, eg. blog_galleries. Once set it is \
typically never changed."
    )

    class Meta:
        unique_together = ((
            "source_content_type", "source_object_id", "target_content_type",
            "target_object_id", "name"
        ),)


def set_managers(sender, **kwargs):
    """
    Make sure all classes have the appropriate managers.
    """
    cls = sender

    if issubclass(cls, ModelBase):
        cls.add_to_class("permitted", PermittedManager())

signals.class_prepared.connect(set_managers)

# Add natural_key to Django's Site model and manager
Site.add_to_class("natural_key", lambda self: (self.domain, self.name))
SiteManager.get_by_natural_key = lambda self, domain, name: self.get(domain=domain, name=name)
