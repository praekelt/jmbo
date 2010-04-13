Django Content:
===============
**Django CMS base content app.**


Utility Methods:
----------------

set_slug:
~~~~~~~~~
set_slug(obj[, text=None, tail_number=0])
Sets a slug on provided object based on text and tail number. A URL friendly slug is generated using django.template.defaultfilters' slugify. Numbers are added to the end of slugs for uniqueness.

*Required arguments*

obj
    An object on which to set the slug. The object must provide a django.db.models.SlugField called **slug**.

*Optional arguments*

text
    text from which to generate slug. If no text is provided the object's id is used.
tail_number
    used internally to create unique slugs.
