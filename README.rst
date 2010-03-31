Django Content:
================
**Django CMS base content app.**

Installation:
-------------
#. Install or add django-content to your python path.
#. Install django-publisher.
#. Add *content* to your INSTALLED_APPS.
#. Add *tagging* to your INSTALLED_APPS.
#. Add *tagging_autocomplete* to your INSTALLED_APPS.
#. Add tagging autocomplete urls project's urls.py file::
    (r'^tagging_autocomplete/', include('tagging_autocomplete.urls')),
#. Sync your database.
