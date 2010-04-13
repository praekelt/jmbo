import time
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

from content.utils import set_slug
from photologue.models import ImageModel

class ModelBase(ImageModel):
    slug = models.SlugField(
        editable=False,
        max_length='512',
        db_index=True,
        unique=True,
    )
    title = models.CharField(
        max_length='256', help_text='A short descriptive title.',
        blank=True,
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
        #null=True,
    )
        
    def save(self, *args, **kwargs):
        # set created time to now on initial save.
        if not self.id and not self.created:
            self.created = datetime.now()
        # set modified to now on each save 
        self.modified = datetime.now()
        
        super(ModelBase, self).save(*args, **kwargs)
        set_slug(self, self.title)
