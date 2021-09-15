from __future__ import absolute_import, unicode_literals

from . import *  # NOQA

ALLOWED_HOSTS = ['*']

DEBUG = True

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

if 'rosetta' not in INSTALLED_APPS:
    try:
        import rosetta
    except ImportError:
        pass
    else:
        INSTALLED_APPS += (
            'rosetta',
        )

if 'django_extensions' not in INSTALLED_APPS:
    try:
        import django_extensions
    except ImportError:
        pass
    else:
        INSTALLED_APPS += (
            'django_extensions',
        )

ROOT_URLCONF = 'mayan.urls.development'

TEMPLATES[0]['OPTIONS']['loaders'] = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

WSGI_AUTO_RELOAD = True
