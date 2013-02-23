DATABASES = {'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': 'autotest.db'}}

INSTALLED_APPS = ('kitabu', 'kitabu.tests',)

MAX_LANE_RESERVATIONS_NR = 5
