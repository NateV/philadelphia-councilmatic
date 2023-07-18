# Leave these blank
OCD_CITY_COUNCIL_NAME = ''
CITY_COUNCIL_NAME = ''
STATIC_PATH = ''
STATIC_ROOT = ''

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'opencivicdata.core.apps.BaseConfig',
    'opencivicdata.legislative.apps.BaseConfig',
    'pupa',
    'councilmatic_core'
)

# Change this if you called your database something different
DATABASE_URL = 'postgres://dev:dev@localhost/philacouncil'
