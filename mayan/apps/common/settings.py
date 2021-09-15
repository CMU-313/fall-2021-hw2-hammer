import os

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

import mayan
from mayan.apps.smart_settings.classes import SettingNamespace

from .literals import DEFAULT_COMMON_HOME_VIEW, LOGGING_HANDLER_OPTIONS

namespace = SettingNamespace(
    label=_('Common'), name='common', version='0002'
)

settings_db_sync_task_delay = namespace.add_setting(
    global_name='COMMON_DB_SYNC_TASK_DELAY',
    default=2,
    help_text=_(
        'Time to delay background tasks that depend on a database commit to '
        'propagate.'
    )
)
setting_disabled_apps = namespace.add_setting(
    global_name='COMMON_DISABLED_APPS',
    default=settings.COMMON_DISABLED_APPS,
    help_text=_(
        'A list of strings designating all applications that are to be removed '
        'from the list normally installed by Mayan EDMS. Each string should be '
        'a dotted Python path to: an application configuration class (preferred), '
        'or a package containing an application.'
    ),
)
setting_extra_apps = namespace.add_setting(
    global_name='COMMON_EXTRA_APPS',
    default=settings.COMMON_EXTRA_APPS,
    help_text=_(
        'A list of strings designating all applications that are installed '
        'beyond those normally installed by Mayan EDMS. Each string should be '
        'a dotted Python path to: an application configuration class (preferred), '
        'or a package containing an application.'
    ),
)
setting_home_view = namespace.add_setting(
    global_name='COMMON_HOME_VIEW',
    default=DEFAULT_COMMON_HOME_VIEW, help_text=_(
        'Name of the view attached to the brand anchor in the main menu. '
        'This is also the view to which users will be redirected after '
        'log in.'
    ),
)
setting_logging_enable = namespace.add_setting(
    global_name='COMMON_LOGGING_ENABLE', default=True, help_text=_(
        'Automatically enable logging to all apps.'
    )
)
setting_logging_handlers = namespace.add_setting(
    global_name='COMMON_LOGGING_HANDLERS', default=('console',),
    help_text=_(
        'List of handlers to which logging messages will be sent. '
        'Options are: {}'.format(', '.join(LOGGING_HANDLER_OPTIONS))
    )
)
setting_logging_level = namespace.add_setting(
    global_name='COMMON_LOGGING_LEVEL', default='ERROR', help_text=_(
        'Level for the logging system.'
    )
)
setting_logging_log_file_path = namespace.add_setting(
    global_name='COMMON_LOGGING_LOG_FILE_PATH',
    default=os.path.join(settings.MEDIA_ROOT, 'error.log'), help_text=_(
        'Path to the logfile that will track errors during production.'
    ),
    is_path=True
)
setting_project_title = namespace.add_setting(
    global_name='COMMON_PROJECT_TITLE',
    default=mayan.__title__, help_text=_(
        'Name to be displayed in the main menu.'
    ),
)
setting_project_url = namespace.add_setting(
    global_name='COMMON_PROJECT_URL',
    default=mayan.__website__, help_text=_(
        'URL of the installation or homepage of the project.'
    ),
)
setting_url_base_path = namespace.add_setting(
    global_name='COMMON_URL_BASE_PATH', default='',
    help_text=_('Base URL path to use for all views.')
)
