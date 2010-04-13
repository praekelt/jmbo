import time

from django.db import models

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
        max_length='256', help_text='A short descriptive title.'
    )
        
    def save(self, *args, **kwargs):
        super(ModelBase, self).save(*args, **kwargs)
        set_slug(self, self.title)
