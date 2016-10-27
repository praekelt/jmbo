"""Patch photologue. There are migrations for this but the patch ensures the
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


def ImageModel_delete(self):
    assert self._get_pk_val() is not None, "%s object can't be deleted because its %s attribute is set to None." % \
        (self._meta.object_name, self._meta.pk.attname)
    self.clear_cache()
    super(ImageModel, self).delete()
    if self.image:
        self.image.storage.delete(self.image.name)

ImageModel.delete = ImageModel_delete


"""Patch photologue create_size so image overrides are considered."""
import os
from io import BytesIO

from django.core.files.base import ContentFile

from photologue.models import Image, PhotoSizeCache


# Copy paste. No idea why it can't also be imported from photologue.models
IMAGE_EXIF_ORIENTATION_MAP = {
    1: 0,
    8: 2,
    3: 3,
    6: 4,
}


def my_create_size(self, photosize):
    if not self.image or self.size_exists(photosize):
        return

    # If we have an override then use it. Prevent circular import.
    from jmbo.models import ModelBase
    if isinstance(self, ModelBase):
        from jmbo.models import ImageOverride
        override = ImageOverride.objects.filter(
            target=self.modelbase_obj, photosize=photosize
        ).first()
        image_model_obj = override if override else self
    else:
        image_model_obj = self

    try:
        im = Image.open(image_model_obj.image.storage.open(image_model_obj.image.name))
    except IOError:
        return
    # Save the original format
    im_format = im.format
    # Apply effect if found
    if image_model_obj.effect is not None:
        im = image_model_obj.effect.pre_process(im)
    elif photosize.effect is not None:
        im = photosize.effect.pre_process(im)
    # Resize/crop image
    if im.size != photosize.size and photosize.size != (0, 0):
        im = image_model_obj.resize_image(im, photosize)
    # Apply watermark if found
    if photosize.watermark is not None:
        im = photosize.watermark.post_process(im)
    # Apply effect if found
    if image_model_obj.effect is not None:
        im = image_model_obj.effect.post_process(im)
    elif photosize.effect is not None:
        im = photosize.effect.post_process(im)
    # Save file
    im_filename = getattr(image_model_obj, "get_%s_filename" % photosize.name)()
    try:
        buffer = BytesIO()
        if im_format != 'JPEG':
            im.save(buffer, im_format)
        else:
            im.save(buffer, 'JPEG', quality=int(photosize.quality),
                    optimize=True)
        buffer_contents = ContentFile(buffer.getvalue())
        image_model_obj.image.storage.save(im_filename, buffer_contents)
    except IOError as e:
        if image_model_obj.image.storage.exists(im_filename):
            image_model_obj.image.storage.delete(im_filename)
        raise e

ImageModel.create_size = my_create_size


def my_get_filename_for_size(self, size):
    photosize = PhotoSizeCache().sizes.get(size)

    from jmbo.models import ModelBase
    if isinstance(self, ModelBase):
        from jmbo.models import ImageOverride
        override = ImageOverride.objects.filter(
            target=self.modelbase_obj, photosize=photosize
        ).first()
        image_model_obj = override if override else self
    else:
        image_model_obj = self

    size = getattr(size, 'name', size)
    base, ext = os.path.splitext(image_model_obj.image_filename())
    return ''.join([base, '_', size, ext])

ImageModel._get_filename_for_size = my_get_filename_for_size
