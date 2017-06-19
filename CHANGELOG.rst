Changelog
=========

3.0.2
-----
#. Use `django-sortedm2m` because it does proper sorting at ORM level.

3.0.1
-----
#. Compatibility with Django Rest Framework 3.6

3.0.0
-----
#. Django 1.9 - 1.11 compatibility.
#. This release deprecates the items marked for deprecation in the 2.x versions.

2.0.17
------
#. Fixed an issue where the patched photologue may flip the image.

2.0.16
------
#. Special migration handling for a special database - Oracle.

2.0.15
------
#. Move to tox for unit testing.

2.0.14
------
#. Add indexes for ``title`` and ``description`` fields.

2.0.13
------
#. Add database index to ``state``.

2.0.12
------
#. Safe handling for missing image on an object.

2.0.11
------
#. The fix for 2.0.10 was incomplete. Fix it properly.

2.0.10
------
#. Fix missing ``USE_GIS`` in migrations. It would always try to pull in django-atlas without it.

2.0.9
-----
#. Add a model that allows a specific curated image to override a scale that would normally be generated.

2.0.8
-----
#. The ``ObjectDetail`` view now respects template_name set at class level.

2.0.7
-----
#. Simplify template inclusion tags.
#. The detail and list views now respect the model attribute.

2.0.6
-----
#. Make object detail template resolution follow the standard Django naming conventions. Backward compatibility is preserved.
#. Move test templates into tests directory.
#. Add dependency on ``django-ultracache`` and defer ``jmbocache`` template tag to ``ultracache`` template tag.

2.0.5
-----
#. Gracefully handle missing images in the API.
#. Change the site information in the unicode method to be less overwhelming.
#. Use built-in jQuery for autosave function.

2.0.4
-----
#. Patch ImageModel delete to handle null image.

2.0.3
-----
#. Limit photologue to <3.2 because they have stopped supporting Django 1.6.

2.0.2
-----
#. Disable more filters so Oracle can work.

2.0.1
-----
#. Disable advanced admin change list filtering if Oracle is the database. The Oracle adapter is buggy.

2.0.0
-----
#. Allow per content type customization of object header and footer.
#. Select all sites initially for new items.
#. The API now dereferences resource URI to the leaf class if possible.
#. Ensure image field is optional on ModelBase database table as well.

2.0.0a1
-------
#. Move to Django 1.6 support. Django 1.4 support is deprecated. For Django 1.4 use Jmbo 1.x.
#. Add `Clone this item` button to change forms.
#. Deprecate gizmo, "wide" template, Pin class.
#. Deprecate own class based generic views in favour of Django's equivalent.
#. Deprecate views related to show objects per category. `jmbo-foundry` offers a much more powerful solution and scales better.
#. Limit Relation change form to only ModelBase subclasses.
#. Deprecate smart_url template tag because Django url template tag does the same now.
#. Move back to mainline `django-photologue`.
#. API now includes image detail url.

1.2.0
-----
#. Use renamed django-photologue-praekelt.
#. SEO optimizations in templates.
#. Make it possible to reach a detail page through a category.

1.1.7
-----
#. Bump to resolve missing version bump in setup.py.

1.1.6
-----
#. API now includes image detail url.
#. URL pattern to resolve detail page through category.

1.1.5
-----
#. Ignore result of celery tasks as appropriate.

1.1.4
-----
#. Relax uniqueness constraint on slugs.

1.1.3
-----
#. Fix modelbase editing where location field was added to wrong fieldset.

1.1.2
-----
#. Add logging to `jmbocache` template tag.

1.1.1
-----
#. Add a template `base.html` so unit tests that render detail pages work.
#. Reshuffle the test layout.

1.1
---
#. Location aware functionality now only takes effect if both 'django-atlas` and `django.contrib.gis` are installed.
#. `django-photologue` 2.10 is now the minimum version.

1.0.14
------
#. Add `rel="nofollow"` on view modifier links.
#. Fix `render_object` where context was copied instead of using push and pop.
#. Simplify sharing link creation.

1.0.13
------
#. Fix a broken find link in `setup.py`.

1.0.12
------
#. Fix incorrect file permissions.

1.0.11
------
#. Add functionality to periodically autosave certain fields on the change form.
#. Change change list ordering to be `-publish_on, -created`.
#. Change `get_related_items` ordering to be `-publish_on, -created`.
#. Use a celery task to publish content.
#. Permalink now links to all sites.

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

