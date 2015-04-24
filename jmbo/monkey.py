"""Patch photologue. There are migrations for this but the patch ensure the
tests pass, because tests skip South migrations."""

from photologue.models import ImageModel, PhotoSize


ImageModel._meta.get_field("image").blank = True
ImageModel._meta.get_field("image").null = True
PhotoSize._meta.get_field("name").max_length = 64


# More patches to handle null image
def ImageModel_decorator(func):
    def new(self, *args, **kwargs):
        if not self.image:
            return
        return func(self, *args, **kwargs)
    return new

ImageModel.create_size = ImageModel_decorator(ImageModel.create_size)
ImageModel.remove_size = ImageModel_decorator(ImageModel.remove_size)
