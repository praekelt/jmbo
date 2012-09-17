import types
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import comments
from django.contrib.sites.models import Site, SiteManager
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db import models
from django.db.models import signals, Sum
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.utils import timezone

from atlas.models import Location
from photologue.models import ImageModel
from preferences import Preferences
import secretballot
from secretballot.models import Vote
from jmbo.managers import PermittedManager, DefaultManager
from jmbo.utils import generate_slug
import jmbo.signals


class JmboPreferences(Preferences):
    __module__ = 'preferences.models'


class ModelBase(ImageModel):
    objects = DefaultManager()
    permitted = PermittedManager()

    state = models.CharField(
        max_length=32,
        choices=(
            ('unpublished', 'Unpublished'),
            ('published', 'Published'),
            ('staging', 'Staging'),
        ),
        default='unpublished',
        editable=False,
        help_text=_("Set the item state. The 'Published' state makes the item \
visible to the public, 'Unpublished' retracts it and 'Staging' makes the \
item visible on staging instances."),
        blank=True,
        null=True,
    )
    publish_on = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        help_text=_("Date and time on which to publish this item (state will \
change to 'published')."),
    )
    retract_on = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        help_text=_("Date and time on which to retract this item (state will \
change to 'unpublished')."),
    )
    slug = models.SlugField(
        editable=False,
        max_length=255,
        db_index=True,
        unique=True,
    )
    title = models.CharField(
        _("Title"),
        max_length=200, help_text=_('A short descriptive title.'),
    )
    subtitle = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        default='',
        help_text=_('Some titles may be the same and cause confusion in admin \
UI. A subtitle makes a distinction.'),
    )
    description = models.TextField(
        help_text=_('A short description. More verbose than the title but \
limited to one or two sentences.'),
        blank=True,
        null=True,
    )
    created = models.DateTimeField(
        _('Created Date & Time'),
        blank=True,
        help_text=_('Date and time on which this item was created. This is \
automatically set on creation, but can be changed subsequently.')
    )
    modified = models.DateTimeField(
        _('Modified Date & Time'),
        editable=False,
        help_text=_('Date and time on which this item was last modified. This \
is automatically set each time the item is saved.')
    )
    owner = models.ForeignKey(
        User,
        blank=True,
        null=True,
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
        'category.Category',
        blank=True,
        null=True,
        help_text=_('Categorizing this item.')
    )
    primary_category = models.ForeignKey(
        'category.Category',
        blank=True,
        null=True,
        help_text=_("Primary category for this item. Used to determine the \
            object's absolute/default URL."),
        related_name="primary_modelbase_set",
    )
    tags = models.ManyToManyField(
        'category.Tag',
        blank=True,
        null=True,
        help_text=_('Tag this item.')
    )
    sites = models.ManyToManyField(
        'sites.Site',
        blank=True,
        null=True,
        help_text=_('Makes item eligible to be published on selected sites.'),
    )
    publishers = models.ManyToManyField(
        'publisher.Publisher',
        blank=True,
        null=True,
        help_text=_(
            'Makes item eligible to be published on selected platform.'
        ),
    )
    comments_enabled = models.BooleanField(
        verbose_name=_("Commenting Enabled"),
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
    location = models.ForeignKey(
        Location,
        blank=True,
        null=True,
        help_text=_("A location that can be used for content filtering."),
    )

    class Meta:
        ordering = ('-created',)

    def as_leaf_class(self):
        """
        Returns the leaf class no matter where the calling instance is in
        the inheritance hierarchy.
        Inspired by http://www.djangosnippets.org/snippets/1031/
        """
        try:
            instance = self.__getattribute__(self.class_name.lower())
        except AttributeError:
            content_type = self.content_type
            model = content_type.model_class()
            if(model == ModelBase):
                return self
            instance = model.objects.get(id=self.id)
        '''
        If distance was dynamically added to this object,
        it needs to be added to the leaf object as well
        '''
        if hasattr(self, "distance"):
            instance.distance = self.distance
        return instance

    def get_absolute_url(self):
        # Use jmbo naming convention, eg. we may have a view named
        # 'post_object_detail'.
        try:
            return reverse(
                '%s_object_detail' \
                    % self.as_leaf_class().__class__.__name__.lower(),
                kwargs={'slug': self.slug}
            )
        except NoReverseMatch:
            # Fallback
            return reverse('object_detail', args=[self.slug])

    def get_absolute_category_url(self):
        """Category aware absolute url"""
        if self.primary_category:
            category_slug = self.primary_category.slug
        elif self.categories.all().exists():
            category_slug = self.categories.all()[0].slug

        if category_slug:
            try:
                return reverse(
                    '%s_category_object_detail' \
                        % self.as_leaf_class().__class__.__name__.lower(),
                    kwargs={'category_slug': category_slug, 'slug': self.slug}
                )
            except NoReverseMatch:
                # Fallback
                return reverse(
                    'category_object_detail',
                    kwargs={'category_slug': category_slug, 'slug': self.slug}
                )

        # Sane fallback if no category
        return self.get_absolute_url()

    def save(self, *args, **kwargs):
        now = timezone.now()

        # set created time to now if not already set.
        if not self.created:
            self.created = now

        # set modified to now on each save.
        self.modified = now

        # set leaf class content type
        if not self.content_type:
            self.content_type = ContentType.objects.get_for_model(\
                    self.__class__)

        # set leaf class class name
        if not self.class_name:
            self.class_name = self.__class__.__name__

        # set title as slug uniquely
        self.slug = generate_slug(self, self.title)

        super(ModelBase, self).save(*args, **kwargs)

    def __unicode__(self):
        if self.subtitle:
            return '%s (%s)' % (self.title, self.subtitle)
        else:
            return self.title

    @property
    def is_permitted(self):
        def for_site():
            if self.sites.filter(id__exact=settings.SITE_ID):
                return True
            else:
                return False

        if self.state == 'unpublished':
            return False
        elif self.state == 'published':
            return for_site()
        elif self.state == 'staging':
            if getattr(settings, 'STAGING', False):
                return for_site()

        return False

    @property
    def modelbase_obj(self):
        if self.__class__ == ModelBase:
            return self
        else:
            '''
            Use self._meta.get_ancestor_link instead of self.modelbase_ptr since 
            the name of the link could be different
            '''
            link_name = self._meta.get_ancestor_link(ModelBase).name
            return getattr(self, link_name)
            

    def can_vote(self, request):
        """
        Determines whether or not the current user can vote.
        Returns a bool as well as a string indicating the current vote status,
        with vote status being one of: 'closed', 'disabled',
        'auth_required', 'can_vote', 'voted'
        """
        modelbase_obj = self.modelbase_obj

        # can't vote if liking is closed
        if modelbase_obj.likes_closed:
            return False, 'closed'

        # can't vote if liking is disabled
        if not modelbase_obj.likes_enabled:
            return False, 'disabled'

        # anonymous users can't vote if anonymous likes are disabled
        if not request.user.is_authenticated() and not \
                modelbase_obj.anonymous_likes:
            return False, 'auth_required'

        # return false if existing votes are found
        if Vote.objects.filter(
            object_id=modelbase_obj.id,
            token=request.secretballot_token
        ).count() == 0:
            return True, 'can_vote'
        else:
            return False, 'voted'

    def can_comment(self, request):
        modelbase_obj = self.modelbase_obj

        # can't comment if commenting is closed
        if modelbase_obj.comments_closed:
            return False, 'closed'

        # can't comment if commenting is disabled
        if not modelbase_obj.comments_enabled:
            return False, 'disabled'

        # anonymous users can't comment if anonymous comments are disabled
        if not request.user.is_authenticated() and not \
                modelbase_obj.anonymous_comments:
            return False, 'auth_required'

        return True, 'can_comment'

    @property
    def vote_total(self):
        """
        Calculates vote total (+1 for upvote and -1 for downvote). We are
        adding a method here instead of relying on django-secretballot's
        addition since that doesn't work for subclasses.
        """
        votes = Vote.objects.filter(object_id= \
            self.id).aggregate(Sum('vote'))['vote__sum']
        return votes if votes else 0

    @property
    def comment_count(self):
        """
        Counts total number of comments on ModelBase object.
        Comments should always be recorded on ModelBase objects.
        """
        # Get the comment model.
        comment_model = comments.get_model()

        modelbase_content_type = ContentType.objects.get(
            app_label="jmbo",
            model="modelbase"
        )

        # Create a qs filtered for the ModelBase or content_type objects.
        qs = comment_model.objects.filter(
            content_type__in=[self.content_type, modelbase_content_type],
            object_pk=smart_unicode(self.pk),
            site__pk=settings.SITE_ID,
        )

        # The is_public and is_removed fields are implementation details of the
        # built-in comment model's spam filtering system, so they might not
        # be present on a custom comment model subclass. If they exist, we
        # should filter on them.
        try:
            comment_model._meta.get_field('is_public')
            is_public = True
        except models.FieldDoesNotExist:
            is_public = False
        if is_public:
            qs = qs.filter(is_public=True)

        if getattr(settings, 'COMMENTS_HIDE_REMOVED', True):
            try:
                comment_model._meta.get_field('is_removed')
                is_removed = True
            except models.FieldDoesNotExist:
                is_removed = False
            if is_removed:
                qs = qs.filter(is_removed=False)

        # Return amount of items in qs
        return qs.count()

    @property
    def image_detail_url(self):
        """If a photosize is defined for the content type return the
        corresponding image URL, else return modelbase detail default image
        URL. This allows content types which may typically have images which
        are not landscaped (eg human faces) to define their own sizes."""
        method = 'get_%s_detail_url' % self.as_leaf_class().__class__.__name__.lower()
        if hasattr(self, method):
            return getattr(self, method)()
        else:
            return getattr(self, 'get_modelbase_detail_url')()

    @property
    def image_list_url(self):
        """If a photosize is defined for the content type return the
        corresponding image URL, else return modelbase detail default image
        URL. This allows content types which may typically have images which
        are not landscaped (eg human faces) to define their own sizes."""
        method = 'get_%s_list_url' % self.as_leaf_class().__class__.__name__.lower()
        if hasattr(self, method):
            return getattr(self, method)()
        else:
            return getattr(self, 'get_modelbase_list_url')()

    def get_related_items(self, name, direction='forward'):
        """If direction is forward get items self points to by name name. If
        direction is reverse get items pointing to self to by name name."""
        if direction == 'forward':
            ids = Relation.objects.filter(
                source_content_type=self.content_type,
                source_object_id=self.id,
                name=name
            ).order_by('-target_object_id').values_list(
                'target_object_id', flat=True
            )
            return ModelBase.permitted.filter(id__in=ids)

        elif direction == 'reverse':
            ids = Relation.objects.filter(
                target_content_type=self.content_type,
                target_object_id=self.id,
                name=name
            ).order_by('-source_object_id').values_list(
                'source_object_id', flat=True
            )
            return ModelBase.permitted.filter(id__in=ids)

        else:
            return ModelBase.permitted.none()

    def get_permitted_related_items(self, name, direction='forward'):
        return self.get_related_items(name, direction)

    def natural_key(self):
        return (self.slug, )

    def publish(self):
        if self.state != 'published':
            now = timezone.now()
            self.state = 'published'
            self.publish_on = now
            if self.retract_on and (self.retract_on <= now):
                self.retract_on = None
            self.save()

    def unpublish(self):
        if self.state != 'unpublished':
            self.state = 'unpublished'
            self.retract_on = timezone.now()
            self.save()

    @property
    def template_name_field(self):
        """This hook allows the model to specify a detail template. When we
        move to class-based generic views this magic will disappear."""
        return '%s/%s_detail.html' % (
            self.content_type.app_label, self.content_type.model
        )


class Pin(models.Model):
    content = models.ForeignKey(ModelBase)
    category = models.ForeignKey('category.Category')


class Relation(models.Model):
    """Generic relation between two objects"""
    # todo: this code is too generic and makes querying slow. Refactor to
    # only relate ModelBase to ModelBase. Migration management command will be
    # required.
    source_content_type = models.ForeignKey(
        ContentType, related_name='relation_source_content_type'
    )
    source_object_id = models.PositiveIntegerField()
    source = generic.GenericForeignKey(
        'source_content_type', 'source_object_id'
    )
    target_content_type = models.ForeignKey(
        ContentType, related_name='relation_target_content_type'
    )
    target_object_id = models.PositiveIntegerField()
    target = generic.GenericForeignKey(
        'target_content_type', 'target_object_id'
    )
    name = models.CharField(
        max_length=32,
        db_index=True,
        help_text="A name used to identify the relation. Must be of the form \
blog_galleries. Once set it is typically never changed."
    )

    class Meta:
        unique_together = ((
            'source_content_type', 'source_object_id', 'target_content_type',
            'target_object_id', 'name'
        ),)


def set_managers(sender, **kwargs):
    """
    Make sure all classes have the appropriate managers.
    """
    cls = sender

    if issubclass(cls, ModelBase):
        cls.add_to_class('permitted', PermittedManager())

signals.class_prepared.connect(set_managers)


# add natural_key to Django's Site model and manager
Site.add_to_class('natural_key', lambda self: (self.domain, self.name))
SiteManager.get_by_natural_key = lambda self, domain, name: self.get(domain=domain, name=name)

# enable voting for ModelBase, but specify a different total name
# so ModelBase's vote_total method is not overwritten
secretballot.enable_voting_on(
    ModelBase,
    total_name="secretballot_added_vote_total"
)
