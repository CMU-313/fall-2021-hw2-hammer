from __future__ import absolute_import, unicode_literals

from .development import *  # NOQA

# Stop debug toolbar patching!
# see https://github.com/django-debug-toolbar/django-debug-toolbar/issues/524
DEBUG_TOOLBAR_PATCH_SETTINGS = False

if 'debug_toolbar' not in INSTALLED_APPS:
    INSTALLED_APPS += (
        'debug_toolbar',
    )

MIDDLEWARE = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
) + MIDDLEWARE
