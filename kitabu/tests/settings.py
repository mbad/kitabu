import sys


if 'test' in sys.argv and 'kitabu' in sys.argv:
    from django.conf import settings
    from django.core.management import call_command
    from django.db.models import loading

    settings.DATABASES['default'] = {'ENGINE': 'django.db.backends.sqlite3'}
    settings.INSTALLED_APPS += ('kitabu.tests',)
    loading.cache.loaded = False
    call_command('syncdb', interactive=False, verbosity=0)
