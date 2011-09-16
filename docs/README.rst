Models
------

.. _modelbase:

jmbo.models.ModelBase
*********************

Base content model implementing common content fields and behavior. All Jmbo content models should inherit from this model.

.. _modelbase.fields:

Fields
~~~~~~
    
.. _modelbase.anonymous_comments:
    
anonymous_comments
++++++++++++++++++
Determines whether or not anonymous commenting should be enabled for the object. This is used internally by the :ref:`modelbase.can_comment` method to determine whether or not a requesting user can comment on the object.

.. _modelbase.anonymous_likes:
    
anonymous_likes
+++++++++++++++
Determines whether or not anonymous liking should be enabled for the object. This is used internally by the :ref:`modelbase.can_vote` method to determine whether or not a requesting user can like the object.

.. _modelbase.categories:
    
categories
++++++++++
Many to many relation to :ref:`category.category` objects, used to categorize the object. Categories are high level constructs to be used for grouping and organizing content, thus creating a site’s table of contents.

.. _modelbase.class_name:

class_name
++++++++++
Class name of inheritance leaf class. 
Used internally as part of :ref:`modelbase.as_leaf_class` method to resolve to inheritance leaf class instance.

.. _modelbase.comments_closed:
    
comments_closed
+++++++++++++++
Determines whether or not comments should be closed for the object. Comments will still display but users won't be able to add new comments. This is used internally by the :ref:`modelbase.can_comment` method to determine whether or not a requesting user can comment on the object.

.. _modelbase.comments_enabled:
    
comments_enabled
++++++++++++++++
Determines whether or not comments should be enabled for the object. Comments will not display when disabled. This is used internally by the :ref:`modelbase.can_comment` method to determine whether or not a requesting user can comment on the object.
    
.. _modelbase.content_type:

content_type
++++++++++++
Relation to `django.contrib.contenttypes.models.ContentType <https://docs.djangoproject.com/en/dev/ref/contrib/contenttypes/>`_ for inheritance leaf class' content type.
Used internally as part of :ref:`modelbase.as_leaf_class` method to resolve to inheritance leaf class instance.
    
.. _modelbase.created:

created
+++++++
Date and time on which the object was created. This is automatically set on creation but can be manually changed subsequently.
    
.. _modelbase.description:

description
+++++++++++
A short description. More verbose than :ref:`modelbase.title` but limited to one or two sentences.

.. _modelbase.likes_closed:
    
likes_closed
++++++++++++
Determines whether or not liking should be closed for the object. Likes will still display but users won't be able to add new likes. This is used internally by the :ref:`modelbase.can_vote` method to determine whether or not a requesting user can like the object.
    
.. _modelbase.likes_enabled:
    
likes_enabled
+++++++++++++
Determines whether or not liking should be enabled for the object. Likes will not display when disabled. This is used internally by the :ref:`modelbase.can_vote` method to determine whether or not a requesting user can like the object.
    
.. _modelbase.modified:

modified
++++++++
Date and time on which the object was last modified. This is automatically set each time the object is saved.

.. _modelbase.owner:

owner
+++++
Relation to `django.contrib.auth.model.User <https://docs.djangoproject.com/en/dev/topics/auth/>`_ object of user that created/owns the object.

.. _modelbase.publish_on:

publish_on
++++++++++
Date and time on which to publish the object (state will change to ``published``).

.. _modelbase.publishers:
    
publishers
++++++++++
Many to many relations to :ref:`publisher.publisher` objects making the object eligible to be published to selected platform.
    
.. _modelbase.retract_on:

retract_on
++++++++++
Date and time on which to retract the object (state will change to ``unpublished``).

.. _modelbase.sites:
    
sites
+++++
Many to many relation to `django.contrib.sites.models.Site <https://docs.djangoproject.com/en/dev/ref/contrib/sites/>`_ objects, denotes on which sites the object will be visible. 
This is used internally by the :ref:`modelbase.permitted` manager and :ref:`modelbase.is_permitted` property in conjunction with :ref:`modelbase.state` to determine object visibility.

.. _modelbase.slug:

slug
++++
Unique slug for the object. A slug is automatically  generated and set on creation based on value of the :ref:`modelbase.title` field. All ModelBase objects are guaranteed to have a unique slug.

.. _modelbase.state:

state
+++++
Designates the object's published state. The ``published`` state makes the item visible to the public, ``unpublished`` retracts it and ``staging`` makes the item visible on staging instances. This is used internally by the :ref:`modelbase.permitted` manager and :ref:`modelbase.is_permitted` property in conjunction with :ref:`modelbase.sites` to determine object visibility.

.. _modelbase.tags:
    
tags
++++
Many to many relation to :ref:`category.tag` objects, used to tag the object. Tags are to be used to describe your content in more detail, in essence providing keywords associated with your content. Tags can also be seen as micro-categorization of a site’s content.
    
.. _modelbase.title:

title
+++++
A short descriptive title. The :ref:`modelbase.slug` field is generated based on the value of this field.

.. _modelbase.methods:

Methods & Properties
~~~~~~~~~~~~~~~~~~~~

.. _modelbase.as_leaf_class:

as_leaf_class(self)
+++++++++++++++++++
Returns the inheritance leaf class instance for the object no matter where the calling instance is in the inheritance hierarchy.

.. _modelbase.can_comment:

can_comment(self, request)
++++++++++++++++++++++++++
Determines whether or not the requesting user can comment on the object. Returns ``True`` or ``False`` based on the values of the :ref:`modelbase.anonymous_comments`, :ref:`modelbase.comments_closed` and :ref:`modelbase.comments_enabled` fields.

.. _modelbase.can_vote:

can_vote(self, request)
+++++++++++++++++++++++
Determines whether or not the requesting user can like the object. Returns ``True`` or ``False`` based on the values of the :ref:`modelbase.anonymous_likes`, :ref:`modelbase.likes_closed` and :ref:`modelbase.likes_enabled` fields and whether or not the user has already liked the object. A string is also returned indicating the current vote status, with vote status being one of ``closed``, ``disabled``, ``auth_required``, ``can_vote`` or ``voted``.

.. _modelbase.comment_count:

comment_count(self)
+++++++++++++++++++
Returns the total number of comments recorded on the object's :ref:`modelbase` parent object.

.. note::
    
    Comments should always be recorded on :ref:`modelbase` parent objects.


.. _modelbase.is_permitted:

is_permitted(self)
++++++++++++++++++
Determines whether or not the object is permitted(visible) for the current site, based on the following rules:

#. ``False`` if the object's :ref:`modelbase.state` field's value is ``unpublished``.
#. ``True`` if the object's :ref:`modelbase.sites` field is set to a site corresponding to the ``SITE_ID`` setting **AND** the object's :ref:`modelbase.state` field's value is ``published``.
#. ``True`` if the object's :ref:`modelbase.sites` field is set to a site corresponding to the ``SITE_ID`` setting **AND** the ``STAGING`` setting is ``True`` **AND** the object's :ref:`modelbase.state` field's value is ``published`` or ``staging``.

.. _modelbase.modelbase_obj:

modelbase_obj(self)
+++++++++++++++++++
Returns the :ref:`modelbase` parent instance for the object no matter where the calling instance is in the inheritance hierarchy.

.. _modelbase.vote_total:

vote_total(self)
++++++++++++++++
Returns the total number of likes recorded on the object's :ref:`modelbase` parent object.

.. note::

    Likes should always be recorded on :ref:`modelbase` parent objects.

