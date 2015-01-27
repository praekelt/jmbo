"""Patch photologue PhotoSize name field length. There is also a migration for
it but the patch ensure the tests pass, because tests skio South migrations."""

from photologue.models import ImageModel, PhotoSize


#ImageModel._meta.get_field("image").blank = True
#ImageModel._meta.get_field("image").null = True
PhotoSize._meta.get_field("name").max_length = 64
