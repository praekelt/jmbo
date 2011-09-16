Models
------

jmbo.models.ModelBase
*********************
.. _modelbase:

class ModelBase
~~~~~~~~~~~~~~
Base content model implementing common content fields and behaviour. All Jmbo content models should inherit from this model.

.. _modelbase.state:

ModelBase.state
+++++++++++++++
Designates the object's published state. The *Published* state makes the item visible to the public, *Unpublished* retracts it and *Staging* makes the item visible on staging instances. This is used internally by the :ref:`modelbase.permitted` manager and :ref:`modelbase.is_permitted` method in conjunction with :ref:`modelbase.sites` to determine object visibility.
    
.. _modelbase.publish_on:

ModelBase.publish_on
++++++++++++++++++++
Date and time on which to publish the object (state will change to 'Published').
    
.. _modelbase.retract_on:

ModelBase.retract_on
++++++++++++++++++++
Date and time on which to retract the object (state will change to 'Unpublished').

.. _modelbase.slug:

ModelBase.slug
++++++++++++++
Unique slug for the object. All ModelBase objects are guaranteed to have a unique slug.

.. _modelbase.title:

ModelBase.title
+++++++++++++++
A short descriptive title.
    
.. _modelbase.description:

ModelBase.description
+++++++++++++++++++++
A short description. More verbose than the title but limited to one or two sentences.
    
.. _modelbase.created:

ModelBase.created
+++++++++++++++++
Date and time on which the object was created. This is automatically set on creation but can be manually changed subsequently.
    
.. _modelbase.modified:

ModelBase.modified
++++++++++++++++++
Date and time on which the object was last modified. This is automatically set each time the object is saved.

.. _modelbase.owner:

ModelBase.owner
+++++++++++++++
Relation to ``django.contrib.auth.model.User`` object of user that created/owns the object.
    
.. _modelbase.content_type:

ModelBase.content_type
++++++++++++++++++++++
Relation to ``django.contrib.contenttypes.models.ContentType`` for inheritance leaf class' content type.
Used internally as part of :ref:`modelbase.as_leaf_class` method to resolve to content leaf class.

.. _modelbase.class_name:

ModelBase.class_name
++++++++++++++++++++
Class name of inheritance leaf class. 
Used internally as part of :ref:`modelbase.as_leaf_class` method to resolve to content leaf class.

.. _modelbase.categories:
    
ModelBase.categories
++++++++++++++++++++
Many to many relation to :ref:`category.category` objects, used to categorize the object. Categories are high level constructs to be used for grouping and organizing content, thus creating a site’s table of contents.

.. _modelbase.tags:
    
ModelBase.tags
++++++++++++++
Many to many relation to :ref:`category.tag` objects, used to tag the object. Tags are to be used to describe your content in more detail, in essence providing keywords associated with your content. Tags can also be seen as micro-categorization of a site’s content.
    
.. _modelbase.sites:
    
ModelBase.sites
+++++++++++++++
Many to many relation to ``django.contrib.sites.models.Site`` objects, denotes on which sites the object will be visible. 
This is used internally by the :ref:`modelbase.permitted` manager and :ref:`modelbase.is_permitted` method in conjunction with :ref:`modelbase.state` to determine object visibility.

