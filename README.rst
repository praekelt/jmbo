Django Content
==============
**Django CMS base content app.**


Models:
=======

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

vote_total::

    ModelBase.vote_total
Calculates vote total as total_upvotes - total_downvotes. We are defining a property here instead of relying on django-secretballot's addition since that doesn't work for subclasses.

generate_slug::

    utils.generate_slug(obj, text)
Sets a slug on provided object based on text and tail number. A URL friendly slug is generated using django.template.defaultfilters' slugify. Numbers are added to the end of slugs for uniqueness.

*Required arguments*

obj
    An object on which to set the slug. The object must provide a django.db.models.SlugField called **slug**.

text
    text from which to generate slug.

MANAGERS
********
permitted::
    ModelBase.permitted
Creates a queryset that only contains objects for the current site with the state field set to 'published'. In case settings.STAGING = True, the queryset will also include objects with the state field set to 'staging'.


Tag Reference
=============

Inclusion Tags
--------------

Enable in your templates with the {% load content_inclusion_tags %} tag.

render_object
~~~~~~~~~~~~~
Polymorphically outputs varying simple object templates based on provided object and type.
The template used is determined as follows: <app_label>/inclusion_tags/<model_name>_<type>.html. If a template of that name is not found content/inclusion_tags/modelbase_<type>.html is used by default.

Arguments: object to render, type of template to render 

Sample usage:

    {% render_object object type %}

Template Tags
-------------

Enable in your templates with the {% load content_template_tags %} tag.

filter_menu
~~~~~~~~~~~
Output django-filter filterset menu

Arguments: filterset to render

Sample usage:

    {% filter_menu filterset %}
    
pager
~~~~~
Outputs pagination links.

Arguments: page object.

Sample usage:

    {% pager page_obj %}
    
smart_query_string
~~~~~~~~~~~~~~~~~~
Outputs current GET query string with additions appended. 

Arguments: additions to append, in pairs. Multiple additions can be provided.

Sample usage:

    {% smart_query_string param1 value1 param2 value2 %}

Results in:

    <path>?param1=value1&param2=value2 

If the current request already contains GET values, those are included. For instance if we have a GET value for paging of 2, the result for the example above would be:

    <path>?paging=2&param1=value1&param2=value2


Filtering
=========
Custom filters and filtersets adding custom functionality to the 3rd party django-filter app.

Filters
-------

IntervalFilter
~~~~~~~~~~~~~~
Filters queryset on week (in reality the last 7 days) or month.

    
OrderFilter
~~~~~~~~~~~
Ordering filter ordering queryset items by most-recent(by created) or most-liked(with score being calculated by positive votes).

FilterSets
----------

IntervalOrderFilterSet
~~~~~~~~~~~~~~~~~~~~~~
Filters queryset through an IntervalFilter('interval'). Orders queryset through an OrderFilter('order').
