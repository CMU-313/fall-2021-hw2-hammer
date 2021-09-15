from __future__ import unicode_literals

from django.conf import settings

DEFAULT_LOCK_TIMEOUT_VALUE = 30

DEFAULT_LOCK_TIMEOUT = getattr(
    settings, 'LOCK_MANAGER_DEFAULT_LOCK_TIMEOUT', DEFAULT_LOCK_TIMEOUT_VALUE
)
