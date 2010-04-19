Django Content:
===============
**Django CMS base content app.**


ModelBase:
----------
class models.ModelBase
    
Base Model delivering common CMS type functiopnality through inheritance.
Child classes should provide model fields specific to their requirements.  


API Reference:
~~~~~~~~~~~~~~

FIELDS
******
state
    Set the item state. The 'Published' state makes the item visible to the public, 'Unpublished' retracts it and 'Staging' makes the item visible to staff users.
slug
    Unique URL friendly slug. Not editable.
title
    A short descriptive title.
description
    A short description. More verbose than the title but limited to one or two sentences.
created
    Date and time on which this item was created. This is automatically set on creation, but can be changed subsequently.
modified
    Date and time on which this item was last modified. This is automatically set each time the item is saved.
owner
    Content owner.
content_type
    Content type of the leaf class as provided by the Content Types framework.
class_name
    Class name of the leaf class.
categories
    Categories are used to broadly categorize items in order to determine where they appear a site.
tags
    Keyword tagging.
sites
    Makes item eligible to be published on selected sites.
publishers
    Makes item eligible to be published on selected platform.

METHODS
*******
as_leaf_class::

    ModelBase.as_leaf_class()
Returns the leaf class no matter where the calling instance is in the inheritance hierarchy.

set_slug::

    set_slug(obj[, text=None])
Sets a slug on provided object based on text and tail number. A URL friendly slug is generated using django.template.defaultfilters' slugify. Numbers are added to the end of slugs for uniqueness.

*Required arguments*

obj
    An object on which to set the slug. The object must provide a django.db.models.SlugField called **slug**.

*Optional arguments*

text
    text from which to generate slug. If no text is provided the object's id is used.

MANAGERS
********
permitted::
    ModelBase.permitted
Creates a queryset that only contains objects for the current site with the state field set to 'published'. In case settings.STAGING = True, the queryset will also include objects with the state field set to 'staging'.
