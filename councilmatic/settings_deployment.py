# These are all the settings that are specific to a deployment

import os
import dj_database_url

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]

# SECURITY WARNING: don't run with debug turned on in production!
# Set this to True while you are developing
DEBUG = True if os.environ.get("DEBUG") == "TRUE" else False

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

IS_HEROKU_APP = "DYNO" in os.environ and not "CI" in os.environ
if IS_HEROKU_APP:
    # In production on Heroku the database configuration is derived from the `DATABASE_URL`
    # environment variable by the dj-database-url package. `DATABASE_URL` will be set
    # automatically by Heroku when a database addon is attached to your Heroku app. See:
    # https://devcenter.heroku.com/articles/provisioning-heroku-postgres
    # https://github.com/jazzband/dj-database-url
    DATABASES = {
        "default": dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=True,
            engine="django.contrib.gis.db.backends.postgis",
        ),
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': 'philacouncil',
            'USER': os.environ["LOCALDBUSER"],
            'PASSWORD': os.environ["LOCALDBPASS"],
            'PORT': 5432,
        }
    }


HAYSTACK_URL = os.environ.get("BONSAI_URL") or os.environ["HAYSTACK_URL"]

HAYSTACK_CONNECTIONS = {}
HAYSTACK_CONNECTIONS["default"] = {
    "ENGINE": "haystack.backends.elasticsearch7_backend.Elasticsearch7SearchEngine",
    "URL": HAYSTACK_URL,
    "INDEX_NAME": "philacouncil",
    "SILENTLY_FAIL": False,
    "BATCH_SIZE": 10,
}

# Remember to run python manage.py createcachetable so this will work! 
# developers, set your BACKEND to 'django.core.cache.backends.dummy.DummyCache'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        #'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'councilmatic_cache',
    }
}

# Set this to flush the cache at /flush-cache/{FLUSH_KEY}
FLUSH_KEY = os.environ["FLUSH_KEY"]

# Set this to allow Disqus comments to render
#DISQUS_SHORTNAME = None

# analytics tracking code
#ANALYTICS_TRACKING_CODE = ''

# Google Maps API Key
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

EXTRA_APPS = ()
