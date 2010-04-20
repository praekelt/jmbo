from django.db.utils import IntegrityError
from django.template.defaultfilters import slugify


def generate_slug(obj, text, tail_number=0):
    from content.models import ModelBase
    """
    Sets a slug on object. Object must provide a SlugField called slug.
    URL friendly slugs are generated using django.template.defaultfilters' slugify.
    Numbers are added to the end of slugs for uniqueness.
    """
    # use django slugify filter to slugify
    slug = slugify(text)

    existing_slugs = [item.slug for item in ModelBase.objects.all()]

    tail_number = 0
    new_slug = slug
    while new_slug in existing_slugs:
        new_slug = slugify("%s-%s" % (slug, tail_number))
        tail_number += 1

    return new_slug
