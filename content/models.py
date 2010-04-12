import time

from django.db import models
from django.db.utils import IntegrityError
from django.template.defaultfilters import slugify

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

    def save_slug(self, slug=None, tail_number=0):
        """
        URL friendly slugs are generated using django.template.defaultfilters' slugify.
        Numbers are added to the end of slugs for uniqueness.
        Uniqueness is checked by recursive saves.
        """
        original_slug = self.slug
        # if no slug is provided use object id
        if not slug:
            slug = self.id
        # use django slugify filter to slugify
        slug = slugify(slug)
        try:
            self.slug = slug
            # if a tail is provided append at end of slug
            if tail_number:
                self.slug = slugify("%s-%s" % (slug, tail_number))
            # only save if slug was updated
            if original_slug != slug:
                self.save()
        except IntegrityError:
            # on uniqueness error increment tail and try again
            self.save_slug(slug, tail_number + 1)
        
    def save(self, *args, **kwargs):
        super(ModelBase, self).save(*args, **kwargs)
        self.save_slug(self.title)
