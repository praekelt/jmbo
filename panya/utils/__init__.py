import inspect
import types

from django.db.utils import IntegrityError
from django.template.defaultfilters import slugify

def generate_slug(obj, text, tail_number=0):
    from panya.models import ModelBase
    """
    Returns a new unique slug. Object must provide a SlugField called slug.
    URL friendly slugs are generated using django.template.defaultfilters' slugify.
    Numbers are added to the end of slugs for uniqueness.
    """
    # use django slugify filter to slugify
    slug = slugify(text)

    existing_slugs = [item.slug for item in ModelBase.objects.exclude(id=obj.id)]

    tail_number = 0
    new_slug = slug
    while new_slug in existing_slugs:
        new_slug = slugify("%s-%s" % (slug, tail_number))
        tail_number += 1

    return new_slug

def modify_class(original_class, modifier_class, override=True):
    """
    Adds class methods from modifier_class to original_class.
    If override is True existing methods in original_class are overriden by those provided by modifier_class.
    """
    # get members to add
    modifier_methods = inspect.getmembers(modifier_class, inspect.ismethod)
    
    # set methods
    for method_tuple in modifier_methods:
        name = method_tuple[0]
        method = method_tuple[1]
        if isinstance(method, types.UnboundMethodType):
            if hasattr(original_class, name) and not override:
                return None
            else:
                setattr(original_class, name, method.im_func)
