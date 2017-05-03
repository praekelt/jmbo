"""Register model in another app but with an existing model name"""
from django.db import models

from jmbo.models import ModelBase


class LeafModel(ModelBase):
    pass
