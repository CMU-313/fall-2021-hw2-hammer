from __future__ import unicode_literals

import os

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from mayan.apps.smart_settings import Namespace

namespace = Namespace(name='signatures', label=_('Document signatures'))
setting_storage_backend = namespace.add_setting(
    default='django.core.files.storage.FileSystemStorage',
    global_name='DOCUMENT_SIGNATURES_STORAGE_BACKEND', help_text=_(
        'Path to the Storage subclass to use when storing detached '
        'signatures.'
    )
)
setting_storage_backend_arguments = namespace.add_setting(
    global_name='DOCUMENT_SIGNATURES_STORAGE_BACKEND_ARGUMENTS',
    default={
        'location': os.path.join(settings.MEDIA_ROOT, 'document_signatures')
    }, help_text=_(
        'Arguments to pass to the SIGNATURE_STORAGE_BACKEND. '
    )
)
