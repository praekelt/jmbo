import os


USE_TZ = True

TIME_ZONE = "Africa/Johannesburg"

xDATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "jmbo",
        "USER": "postgres",
        "PASSWORD": "",
        "HOST": "",
        "PORT": "",
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'skeleton.db', # Or path to database file if using sqlite3.
        'USER': 'skeleton', # Not used with sqlite3.
        'PASSWORD': 'skeleton', # Not used with sqlite3.
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    }
}

INSTALLED_APPS = (
    # Include tests because it declares models
    "jmbo.tests",
    "jmbo.tests.extra",
    "jmbo",
    "photologue",
    "category",
    "django_comments",
    "likes",
    "secretballot",
    "pagination",
    "preferences",
    "ultracache",
    "sites_groups",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
)

ROOT_URLCONF = "jmbo.tests.urls"

MIDDLEWARE_CLASSES = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "likes.middleware.SecretBallotUserIpUseragentMiddleware",
    "pagination.middleware.PaginationMiddleware",
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
)

SITE_ID = 1

STATIC_URL = "/static/"

# Disable celery
CELERY_ALWAYS_EAGER = True
BROKER_BACKEND = "memory"

SECRET_KEY = "SECRET_KEY"

TEMPLATE_DIRS = (
    os.path.realpath(os.path.dirname(__file__)) + "/../templates/",
)

# Ultracache triggers lazy creation of content types. This prevents that code
# path.
ULTRACACHE = {"invalidate": False}
