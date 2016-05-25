from django.contrib import admin

from jmbo.admin import ModelBaseAdmin
from jmbo.tests.models import TestModel


admin.site.register(TestModel, ModelBaseAdmin)
