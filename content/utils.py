from django.db.utils import IntegrityError
from django.template.defaultfilters import slugify

def set_slug(obj, text=None, tail_number=0):
    """
    Sets a slug on object. Object must provide a SlugField called slug.
    URL friendly slugs are generated using django.template.defaultfilters' slugify.
    Numbers are added to the end of slugs for uniqueness.
    Uniqueness is checked by recursive saves.
    In case no text is provided use object id.
    """
    original_slug = obj.slug
    # if no slug is provided use object id
    if not text:
        text = obj.id
    # use django slugify filter to slugify
    slug = slugify(text)
    try:
        obj.slug = slug
        # if a tail is provided append at end of slug
        if tail_number:
            obj.slug = slugify("%s-%s" % (slug, tail_number))
        # only save if slug was updated
        if original_slug != slug:
            obj.save()
    except IntegrityError:
        # on uniqueness error increment tail and try again
        set_slug(obj, slug, tail_number + 1)
