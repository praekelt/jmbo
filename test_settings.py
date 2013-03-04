USE_TZ = True

TIME_ZONE = 'Africa/Johannesburg'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.spatialite',
        'NAME': 'jmbo.db',
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
    'django.contrib.gis',
    'atlas',
    'category',
    'jmbo',
    'photologue',
    'secretballot',
    'publisher',
]

SITE_ID = 1
