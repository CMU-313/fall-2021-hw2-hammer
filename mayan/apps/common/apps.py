from __future__ import absolute_import, unicode_literals

import logging
import os
import warnings
from datetime import timedelta
import sys
import traceback

from kombu import Exchange, Queue

from django import apps
from django.conf import settings
from django.conf.urls import include, url
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from mayan.celery import app

from .classes import Template
from .handlers import (
    handler_pre_initial_setup, handler_pre_upgrade,
    handler_user_locale_profile_create,
    handler_user_locale_profile_session_config
)
from .licenses import *  # NOQA
from .links import (
    link_about, link_check_version, link_current_user_locale_profile_edit,
    link_license, link_object_error_list_clear, link_packages_licenses,
    link_setup, link_tools, separator_system
)
from .literals import DELETE_STALE_UPLOADS_INTERVAL, MESSAGE_SQLITE_WARNING
from .menus import (
    menu_about, menu_secondary, menu_topbar, menu_user
)
from .queues import *  # NOQA - Force queues registration
from .settings import (
    setting_auto_logging, setting_production_error_log_path,
    setting_production_error_logging
)
from .signals import pre_initial_setup, pre_upgrade
from .tasks import task_delete_stale_uploads  # NOQA - Force task registration
from .utils import check_for_sqlite
from .warnings import DatabaseWarning

logger = logging.getLogger(__name__)


class MayanAppConfig(apps.AppConfig):
    app_namespace = None
    app_url = None

    def ready(self):
        logger.debug('Initializing app: %s', self.name)
        from mayan.urls import urlpatterns

        if self.app_url:
            top_url = '{}/'.format(self.app_url)
        elif self.app_url is not None:
            top_url = ''
        else:
            top_url = '{}/'.format(self.name)

        try:
            urlpatterns += url(
                r'^{}'.format(top_url),
                include(
                    '{}.urls'.format(self.name),
                    namespace=self.app_namespace or self.name
                )
            ),
        except ImportError as exception:
            if force_text(exception) not in ('No module named urls', 'No module named \'{}.urls\''.format(self.name)):
                logger.exception(
                    'Import time error when running AppConfig.ready() of app '
                    '"%s".', self.name
                )
                exc_info = sys.exc_info()
                traceback.print_exception(*exc_info)
                raise exception


class CommonApp(MayanAppConfig):
    app_namespace = 'common'
    app_url = ''
    has_rest_api = True
    has_tests = True
    name = 'mayan.apps.common'
    verbose_name = _('Common')

    def ready(self):
        super(CommonApp, self).ready()
        if check_for_sqlite():
            warnings.warn(
                category=DatabaseWarning, message=force_text(MESSAGE_SQLITE_WARNING)
            )

        Template(
            name='menu_main', template_name='appearance/menu_main.html'
        )
        Template(
            name='menu_topbar', template_name='appearance/menu_topbar.html'
        )

        app.conf.beat_schedule.update(
            {
                'task_delete_stale_uploads': {
                    'task': 'mayan.apps.common.tasks.task_delete_stale_uploads',
                    'schedule': timedelta(
                        seconds=DELETE_STALE_UPLOADS_INTERVAL
                    ),
                },
            }
        )

        app.conf.task_queues.extend(
            (
                Queue('default', Exchange('default'), routing_key='default'),
                Queue('tools', Exchange('tools'), routing_key='tools'),
                Queue(
                    'common_periodic', Exchange('common_periodic'),
                    routing_key='common_periodic', delivery_mode=1
                ),
            )
        )

        app.conf.task_default_queue = 'default'

        app.conf.task_routes.update(
            {
                'mayan.apps.common.tasks.task_delete_stale_uploads': {
                    'queue': 'common_periodic'
                },
            }
        )
        menu_user.bind_links(
            links=(
                link_current_user_locale_profile_edit,
            ), position=50
        )

        menu_about.bind_links(
            links=(
                link_tools, link_setup, separator_system, link_about,
                link_license, link_packages_licenses, link_check_version
            )
        )

        menu_topbar.bind_links(links=(menu_about, menu_user,), position=99)
        menu_secondary.bind_links(
            links=(link_object_error_list_clear,), sources=(
                'common:object_error_list',
            )
        )

        post_save.connect(
            dispatch_uid='common_handler_user_locale_profile_create',
            receiver=handler_user_locale_profile_create,
            sender=settings.AUTH_USER_MODEL
        )
        pre_initial_setup.connect(
            dispatch_uid='common_handler_pre_initial_setup',
            receiver=handler_pre_initial_setup
        )
        pre_upgrade.connect(
            dispatch_uid='common_handler_pre_upgrade',
            receiver=handler_pre_upgrade
        )

        user_logged_in.connect(
            dispatch_uid='common_handler_user_locale_profile_session_config',
            receiver=handler_user_locale_profile_session_config
        )
        self.setup_auto_logging()

    def setup_auto_logging(self):
        if setting_auto_logging.value:
            if settings.DEBUG:
                level = 'DEBUG'
                handlers = ['console']
            else:
                level = 'ERROR'
                handlers = ['console']

            if os.path.exists(settings.MEDIA_ROOT) and setting_production_error_logging.value:
                handlers.append('logfile')

            loggers = {}
            for project_app in apps.apps.get_app_configs():
                loggers[project_app.name] = {
                    'handlers': handlers,
                    'propagate': True,
                    'level': level,
                }

            logging_configuration = {
                'version': 1,
                'disable_existing_loggers': False,
                'formatters': {
                    'intermediate': {
                        '()': 'mayan.apps.common.log.ColorFormatter',
                        'format': '%(name)s <%(process)d> [%(levelname)s] "%(funcName)s() line %(lineno)d %(message)s"',
                    },
                    'logfile': {
                        'format': '%(asctime)s %(name)s <%(process)d> [%(levelname)s] "%(funcName)s() line %(lineno)d %(message)s"'
                    },
                },
                'handlers': {
                    'console': {
                        'class': 'logging.StreamHandler',
                        'formatter': 'intermediate',
                        'level': 'DEBUG',
                    },
                },
                'loggers': loggers
            }

            if os.path.exists(settings.MEDIA_ROOT) and setting_production_error_logging.value:
                logging_configuration['handlers']['logfile'] = {
                    'backupCount': 3,
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': setting_production_error_log_path.value,
                    'formatter': 'logfile',
                    'maxBytes': 1024,
                }

            logging.config.dictConfig(logging_configuration)
