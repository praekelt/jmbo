Changelog
=========

1.0.10
------
#. Change secretballot usage so it does not hijack the objects manager anymore.
#. Add `owner_override` and `image_attribution` fields.

1.0.9
-----
#. Change permitted manager and generic object detail so staff can preview unpublished content.
#. Aggregate total comments and likes onto `ModelBase` to prevent expensive queries.

1.0.8
-----
#. Add caching template tag `jmbocache` which automatically adds the `SITE_ID` as part of the cache key.

1.0.7
-----
#. Generic caching on detail templates.
#. Share on Google.

1.0.6
-----
#. Add a list filter in admin to filter `ModelBase` objects by site and site group.
#. `ModelBase.__unicode__` includes the site name - non-admin templates that rely on __unicode__ will have to be updated.
#. Set title, description and keywords meta tags on detail page.
#. `comment_count` is now aware that multiple sites may comprise a logical site.

1.0.5
-----
#. Make `jmbo_publish` command timezone-aware, ensuring that it works with old, naive timestamps.

1.0.4
-----
#. Restore crop from field to a more prominent position.

1.0.3
-----
#. Simplify the change form. Move advanced fields into their own section.

1.0.2
-----
#. Ensure the leaf object is passed to template tags in `modelbase_detail.html`.
#. `get_related_items` parameter `name` is now optional. The sorting has changed to reverse on modified (our default sorting).

1.0.1
-----
#. `as_leaf_class` method would break if two models had the same name. Fixed.

1.0
---
#. Jmbo is now location aware. This requires a manual upgrade of libraries and existing databases. DO NOT UPGRADE to 1.0 without preparation. If you are on Ubuntu then it is as simple as running the interactive ``convert_to_geodb_ubuntu.sh`` script.

0.5.5
-----
#. `modelbase_detail` inclusion template now has a block for easier re-use.
#. Simplified paginator. No more breadcrumbs.
#. Introduce `object_footer` template which shows sharing links.
#. ``can_comment`` has an API change. It has always only been used internally and should not cause problems.
#. README.rst gets friendlier documentation.

0.5.4
-----
#. Pin Django on 1.4.x range.

0.5.3
-----
#. Add `Save and publish` and `Save and unpublish` buttons to edit form.

0.5.2
-----
#. Use django.jQuery instead of $ to trigger publish ajax call. $ is not necessarily available.

0.5.1 (2012-08-20)
------------------
#. ``on_likes_enabled_test`` and ``on_can_vote_test`` signal receivers now only checks ``ModelBase`` based objects. Also updated for compatibility with ``django-likes`` 0.0.8, which updated its signal's ``obj`` param to conventional ``instance``. ``django-likes`` >= 0.0.8 is now required for correct operation.

0.5
---
#. Django 1.4 compatible release. Django 1.4 is now required.

0.4
---
#. Detail templates can now be customized per model. Create {app_label}/{model}_detail.html.
#. publish_on and retract_on filters are now applied via management command `jmbo_publish`. Run it via cron.
#. Published state is not directly editable through change form anymore. It is now an action.

0.3.4 (2012-06-26)
------------------
#. Natural key support for dumping and loading data.

0.3.3 (2012-06-20)
------------------
#. Use Pillow instead of PIL.

0.3.2
-----
#. Use slug for lookups in tastypie API.

0.3.1 (2012-06-15)
------------------
#. Add a decorator register_tag that can accept a softcoded list of templates.

0.3 (2012-06-14)
----------------
#. django-tastypie support added

0.2.6 (2012-06-07)
------------------
#. Add image_list_url to Modelbase.
#. Pin django-setuptest to 0.0.6 because of issue in 0.0.7

0.2.5 (2012-05-11)
------------------
#. Admin category filtering now filters on both categories and primary_category fields.

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

