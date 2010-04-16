import time
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

import tagging
from content.utils import set_slug
from photologue.models import ImageModel

class ModelBase(ImageModel):
    state = models.CharField(
        max_length=32,
        choices=(
            ('unpublished', 'Unpublished'),
            ('published', 'Published'),
            ('staging', 'Staging'),
        ),
        default='unpublished',
        help_text="Set the item state. The 'Published' state makes the item visible to the public, 'Unpublished' retracts it and 'Staging' makes the item visible to staff users.",
        blank=True,
        null=True,
    )
    slug = models.SlugField(
        editable=False,
        max_length='512',
        db_index=True,
        unique=True,
    )
    title = models.CharField(
        max_length='256', help_text='A short descriptive title.',
        null=True,
    )
    description = models.TextField(
        help_text='A short description. More verbose than the title but limited to one or two sentences.',
        blank=True,
        null=True,
    )
    created = models.DateTimeField(
        'Created Date & Time', 
        blank=True,
        help_text='Date and time on which this item was created. This is automatically set on creation, but can be changed subsequently.'
    )
    modified = models.DateTimeField(
        'Modified Date & Time', 
        editable=False,
        help_text='Date and time on which this item was last modified. This is automatically set each time the item is saved.'
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
        help_text='Categorizing this item.'
    )
    tags = tagging.fields.TagField()
   
    class Meta:
        ordering = ('-created',)
    
    def as_leaf_class(self):
        """
        Returns the leaf class no matter where the calling instance is in the inheritance hierarchy.
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
        
    def save(self, *args, **kwargs):
        # set created time to now on initial save.
        if not self.id and not self.created:
            self.created = datetime.now()
        # set modified to now on each save 
        self.modified = datetime.now()
       
        # set leaf class content type
        if not self.content_type:
            self.content_type = ContentType.objects.get_for_model(self.__class__)
        
        # set leaf class class name
        if not self.class_name:
            self.class_name = self.__class__.__name__
        
        super(ModelBase, self).save(*args, **kwargs)
        set_slug(self, self.title)
