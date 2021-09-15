from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.smart_settings import Namespace

from .literals import DEFAULT_EXIF_PATH

namespace = Namespace(name='file_metadata', label=_('File metadata'))

setting_drivers_arguments = namespace.add_setting(
    global_name='FILE_METADATA_DRIVERS_ARGUMENTS',
    default={'exif_driver': {'exiftool_path': DEFAULT_EXIF_PATH}}, help_text=_(
        'Arguments to pass to the drivers.'
    )
)
setting_auto_process = namespace.add_setting(
    global_name='FILE_METADATA_AUTO_PROCESS', default=True,
    help_text=_(
        'Set new document types to perform file metadata processing '
        'automatically by default.'
    )
)
