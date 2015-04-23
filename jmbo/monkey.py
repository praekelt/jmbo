"""Patch photologue. There are migrations for this but the patch ensure the
tests pass, because tests skip South migrations."""

from photologue.models import ImageModel, PhotoSize


ImageModel._meta.get_field("image").blank = True
ImageModel._meta.get_field("image").null = True
PhotoSize._meta.get_field("name").max_length = 64
