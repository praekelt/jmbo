import os


USE_TZ = True

TIME_ZONE = 'Africa/Johannesburg'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'jmbo',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

INSTALLED_APPS = (
    'jmbo',
    'photologue',
    'category',
    'likes',
    'secretballot',
    'pagination',
    'publisher',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.comments',
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'south',
)

ROOT_URLCONF = 'jmbo.tests.urls'

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'likes.middleware.SecretBallotUserIpUseragentMiddleware',
    'pagination.middleware.PaginationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)

SITE_ID = 1

STATIC_URL = '/static/'

# Disable celery
CELERY_ALWAYS_EAGER = True
BROKER_BACKEND = 'memory'

SECRET_KEY = 'SECRET_KEY'

STAGING = False

# xxx: get tests to pass with migrations
SOUTH_TESTS_MIGRATE = False

TEMPLATE_DIRS = (
    os.path.realpath(os.path.dirname(__file__)) + '/../templates/',
)
