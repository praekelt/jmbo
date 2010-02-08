# python imports
from datetime import datetime

# djanog imports
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template import defaultfilters

# 3rd party imports
from photologue.models import ImageModel

# our app imports
from publisher.models import Publisher

# Utility Functions
def slugify(self):
    """
    URL friendly slugs are generated using django.template.defaultfilters' slugify.
    Numbers are added to the end of slugs for uniqueness.
    """
    # get the title from either the title or the id
    title = getattr(self, 'title', None) or self.id

    # slugify with the default django filter
    slug = defaultfilters.slugify(title)
    if self.slug == slug:
        return slug
    
    #check to see if slug exists, increment slug tail if it does
    slugs = [content.slug for content in ModelBase.objects.all()]
    i = 1
    numbered_slug = slug
    while numbered_slug in slugs:
        numbered_slug = "%s-%s" % (slug, i)
        i += 1
    return numbered_slug

# Models
class ModelBase(Publisher):
    """
    ALL objects used on a Content system should inherit from ModelBase.
    ModelBase is a lightweight baseclass adding extra functionality not offered natively by Django.
    It should be seen as adding value to child classes primarily through functions.
    Child classes should provide model fields specific to their requirements.  
    """
    slug = models.SlugField(
        editable=False,
        max_length='275',
        db_index=True,
    )
    content_type = models.ForeignKey(
        ContentType, 
        editable=False, 
        null=True
    )
    classname = models.CharField(
        max_length=32, 
        editable=False, 
        null=True
    )

    def save(self, *args, **kwargs):
        if(not self.content_type):
            self.content_type = ContentType.objects.get_for_model(self.__class__)
        self.classname = self.__class__.__name__
        if not self.slug:
            self.slug = slugify(self)
        super(ModelBase, self).save(*args, **kwargs)
    
    def as_leaf_class(self):
        """
        Inspired by http://www.djangosnippets.org/snippets/1031/
        """
        try:
            return self.__getattribute__(self.classname.lower())
        except AttributeError:
            content_type = self.content_type
            model = content_type.model_class()
            if(model == ModelBase):
                return self
            return model.objects.get(id=self.id)

    def delete(self, *args, **kwargs):
        for related in self._meta.get_all_related_objects():
            cascade = getattr(related.model, '_cascade', True)
            if not cascade:
                field = getattr(self, related.get_accessor_name())
                field.clear()
        super(ModelBase, self).delete(*args, **kwargs)

    def __unicode__(self):
        if self.__class__ == ModelBase:
            try:
                return self.as_leaf_class().__unicode__()
            except: 
                return self.slug
        else: 
            return self.slug

class ContentBase(ModelBase, ImageModel):
    title = models.CharField(
        max_length='256', help_text='A short descriptive title.'
    )
    description = models.TextField(
        help_text='A short description. More verbose than the title but limited to one or two sentences.'
    )
    created = models.DateTimeField(
        'Created Date & Time', blank=True,
        help_text='Date and time on which this item was created. This is automatically set on creation, but can be changed subsequently.'
    )
    modified = models.DateTimeField(
        'Modified Date & Time', editable=False,
        help_text='Date and time on which this item was last modified. This is automatically set each time the item is saved.'
    )
    rating = models.IntegerField(
        blank=True,
        null=True,
        choices=[(n, str(n)) for n in range(1,6)],
        help_text='Rating for this item.',
    )
    owner = models.ForeignKey(
        User, 
        blank=True,
        null=True,
    )

    def save(self, *args, **kwargs):
        """
        Set created time on initial save.
        """
        if not self.id and not self.created:
            self.created = datetime.now()
        self.modified = datetime.now()
        super(ContentBase, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title
