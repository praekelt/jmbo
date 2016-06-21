import logging

from django.conf import settings


logger = logging.getLogger("django")

if settings.REST_FRAMEWORK.get("DEFAULT_VERSIONING_CLASS") != \
    "rest_framework.versioning.URLPathVersioning":
    logger.warning("""Jmbo: URLPathVersioning is not set as \
DEFAULT_VERSIONING_CLASS. It is strongly recommended to update your \
settings.""")
