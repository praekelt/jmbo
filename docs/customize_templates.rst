Customizing templates
*********************

Custom templates can be created for the following:

*   Individual models that extend ModelBase
*   All application models that extend ModelBase

Objects extending ModelBase
===========================
Create templates and inclusion_tags folders.

In your app folder you require the following folder structure:

*   *<app name>/templates/jmbo/inclusion_tags/*


Create templates to override
++++++++++++++++++++++++++++

Create template html files inside:

*   *<app name>/templates/jmbo/inclusion_tags/object_<type>.html*

Creating object templates in this folder will override all objects that extend ModelBase.

ex. creating object_header.html and editing its content will change
what is displayed on your page headers.

Default templates
+++++++++++++++++

.. toctree::
   :maxdepth: 2

   inclusion_tags

App specific models
===================

The folder structure changes slightly.

*   *<app name>/templates/<app name>/inclusion_tags/object_<type>.html*

This will override all Models that extend ModelBase in the app,
while external ModelBase objects can still be overriden seperately.

Alternatively each app Model can also be overriden to use their own seperate templates.


Individual models
=================
The template naming convention changes slightly.

*   *<app name>/templates/<app name>/inclusion_tags/<model>_<type>.html*

Instead of generic object templates, model specific templates are now used.

Template resolution
===================

Modelbase templates get resolved in the following order:

#.   *<app name>/inclusion_tags/<model>_<type>.html*
#.   *<app name>/<model>/inclusion_tags/object_<type>.html*
#.   *<app name>/inclusion_tags/object_<type>.html*
#.   *jmbo/inclusion_tags/object_<type>.html*

The list from top to bottom lists the order in which templates are found and resolved.
Paths that are higher up take priority and are rendered.
If template is not found in any of these paths a default tempalte is used.
