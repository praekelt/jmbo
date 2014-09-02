USE_TZ = True

TIME_ZONE = 'Africa/Johannesburg'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'jmbo',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.comments',
    'django.contrib.contenttypes',
    'django.contrib.sites',
#    'django.contrib.gis',
#    'atlas',
    'category',
    'jmbo',
    'photologue',
    'secretballot',
    'publisher',
    'south',
]

SITE_ID = 1

# Disable celery
CELERY_ALWAYS_EAGER = True
BROKER_BACKEND = 'memory'

# xxx: get tests to pass with migrations
SOUTH_TESTS_MIGRATE = False
