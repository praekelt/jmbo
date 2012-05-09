Changelog
=========

0.2.4
-----
#. Remove dependency links in setup.py.

0.2.3 (2012-05-08)
------------------
#. render_object tag now fails with clear TemplateDoesNot exist exception.

0.2.2
-----
#. Include category filtering in admin.

0.2.1
-----
#. Find links in setup.py

0.2
---
#. Add Opengraph metadata tags to detail view.
#. Add dependency on django-sites-groups.
#. Setup South migration chain.

0.1.20
------
#. Bring pager HTML and CSS in line with django-pagination.
#. Add wrapping div to comments UI.
#. Fix admin interface bug where some fields were duplicated.
#. Reverse lookup for <content_type>_object_detail now works for model names that may contain spaces, eg. 'Blog Post'.
#. Add fallback to modelbase detail view to get_absolute_url.
#. Add ability to limit size of queryset for generic views.
#. Afrikaans and French translations.
#. Make it possible to specify a custom photosize per content type.
#. Introduce a new optional field 'subtitle' for friendlier admin UI.
#. Add South migrations. Existing installations must be upgraded using ./manage.py migrate jmbo 0001 --fake and then ./manage.py migrate jmbo.

0.1.9 (2011-09-27)
------------------
#. Added primary category field on ModelBase.
#. Allow for modifier on humanize time diff tag.
#. Added category pin model and admin override.

0.1.7 (2011-06-15)
------------------
#. Jmbo rename.

0.1.6
-----
#. Added state admin bulk actions.

0.1.5
-----
#. Use photologue 2.6.praekelt

0.1.4
-----
#. Generate slug optimization.

0.1.3
-----
#. Refactored ModelBase.comment_count to resolve comments for leaf class or modelbase content types.

0.1.2
-----
#. Generic form issues corrected.

0.1.1
-----
#. Use django-photologue 2.5.praekelt

0.1.0
-----
#. Improved generate_slug utils method.
#. Removed ModelBaseAdminForm.

