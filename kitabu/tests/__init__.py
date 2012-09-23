import sys


if 'test' in sys.argv and 'kitabu' in sys.argv:
    #from django.core.management import call_command
    #from django.db.models import loading

    #loading.cache.loaded = False
    #call_command('syncdb', interactive=False, verbosity=0)

    from kitabu.tests.tests import *
    from kitabu.tests.forms.availability import *
