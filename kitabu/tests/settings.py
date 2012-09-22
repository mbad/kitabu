print 'loading kitabu settings for automated tests'

DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': 'autotest.db',
}

INSTALLED_APPS += ('kitabu.tests',)
