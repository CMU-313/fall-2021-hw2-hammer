from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from kombu import Exchange, Queue

from mayan.apps.common import (
    MayanAppConfig, MissingItem, menu_list_facet, menu_object, menu_secondary,
    menu_setup
)
from mayan.apps.common.signals import post_initial_setup, post_upgrade
from mayan.apps.common.widgets import TwoStateWidget
from mayan.apps.converter.links import link_transformation_list
from mayan.apps.documents.menus import menu_documents
from mayan.apps.documents.signals import post_version_upload
from mayan.apps.navigation import SourceColumn
from mayan.celery import app

from .classes import StagingFile
from .handlers import (
    handler_copy_transformations_to_version,
    handler_create_default_document_source, handler_initialize_periodic_tasks
)
from .links import (
    link_document_create_multiple, link_source_check_now,
    link_source_create_imap_email, link_source_create_pop3_email,
    link_source_create_sane_scanner,
    link_source_create_staging_folder,
    link_source_create_watch_folder, link_source_create_webform,
    link_source_delete, link_source_edit, link_source_logs,
    link_source_list, link_staging_file_delete, link_upload_version
)
from .queues import *  # NOQA
from .widgets import StagingFileThumbnailWidget


class SourcesApp(MayanAppConfig):
    app_namespace = 'sources'
    app_url = 'sources'
    has_rest_api = True
    has_tests = True
    name = 'mayan.apps.sources'
    verbose_name = _('Sources')

    def ready(self):
        super(SourcesApp, self).ready()

        POP3Email = self.get_model(model_name='POP3Email')
        IMAPEmail = self.get_model(model_name='IMAPEmail')
        Source = self.get_model(model_name='Source')
        SourceLog = self.get_model(model_name='SourceLog')
        SaneScanner = self.get_model(model_name='SaneScanner')
        StagingFolderSource = self.get_model(model_name='StagingFolderSource')
        WatchFolderSource = self.get_model(model_name='WatchFolderSource')
        WebFormSource = self.get_model(model_name='WebFormSource')

        MissingItem(
            condition=lambda: not Source.objects.exists(),
            description=_(
                'Document sources are the way in which new documents are '
                'feed to Mayan EDMS, create at least a web form source to '
                'be able to upload documents from a browser.'
            ),
            label=_('Create a document source'),
            view='sources:source_list'
        )

        SourceColumn(
            attribute='label', is_identifier=True, is_sortable=True,
            source=Source
        )
        SourceColumn(
            attribute='class_fullname', label=_('Type'), source=Source
        )
        SourceColumn(
            attribute='enabled', is_sortable=True, source=Source,
            widget=TwoStateWidget
        )

        SourceColumn(
            attribute='get_date_time_created', label=_('Created'),
            source=StagingFile
        )
        html_widget = StagingFileThumbnailWidget()
        SourceColumn(
            func=lambda context: html_widget.render(
                instance=context['object'],
            ),
            label=_('Thumbnail'),
            source=StagingFile
        )

        SourceColumn(
            attribute='datetime', is_identifier=True, label=_('Date and time'),
            source=SourceLog
        )
        SourceColumn(
            attribute='message', label=_('Text'), source=SourceLog
        )

        app.conf.task_queues.extend(
            (
                Queue(
                    'sources', Exchange('sources'), routing_key='sources'
                ),
                Queue(
                    'sources_fast', Exchange('sources_fast'),
                    routing_key='sources_fast', delivery_mode=1
                ),
                Queue(
                    'sources_periodic', Exchange('sources_periodic'),
                    routing_key='sources_periodic', delivery_mode=1
                ),
            )
        )

        app.conf.task_routes.update(
            {
                'mayan.apps.sources.tasks.task_check_interval_source': {
                    'queue': 'sources_periodic'
                },
                'mayan.apps.sources.tasks.task_generate_staging_file_image': {
                    'queue': 'sources_fast'
                },
                'mayan.apps.sources.tasks.task_source_handle_upload': {
                    'queue': 'sources'
                },
                'mayan.apps.sources.tasks.task_upload_document': {
                    'queue': 'sources'
                },
            }
        )
        menu_documents.bind_links(links=(link_document_create_multiple,))

        menu_list_facet.bind_links(
            links=(
                link_source_logs, link_transformation_list,
            ), sources=(
                POP3Email, IMAPEmail, SaneScanner, StagingFolderSource,
                WatchFolderSource, WebFormSource
            )
        )

        menu_object.bind_links(
            links=(
                link_source_edit, link_source_delete,
            ), sources=(
                POP3Email, IMAPEmail, SaneScanner, StagingFolderSource,
                WatchFolderSource, WebFormSource
            )
        )
        menu_object.bind_links(
            links=(link_staging_file_delete,), sources=(StagingFile,)
        )
        menu_object.bind_links(
            links=(link_source_check_now,),
            sources=(IMAPEmail, POP3Email, WatchFolderSource,)
        )
        menu_secondary.bind_links(
            links=(
                link_source_list, link_source_create_webform,
                link_source_create_sane_scanner,
                link_source_create_staging_folder,
                link_source_create_pop3_email,
                link_source_create_imap_email,
                link_source_create_watch_folder
            ), sources=(
                POP3Email, IMAPEmail, StagingFolderSource, WatchFolderSource,
                WebFormSource, 'sources:source_list',
                'sources:source_create'
            )
        )
        menu_setup.bind_links(links=(link_source_list,))
        menu_secondary.bind_links(
            links=(link_upload_version,),
            sources=(
                'documents:document_version_list', 'documents:upload_version',
                'documents:document_version_revert'
            )
        )

        post_upgrade.connect(
            dispatch_uid='sources_handler_initialize_periodic_tasks',
            receiver=handler_initialize_periodic_tasks
        )
        post_initial_setup.connect(
            dispatch_uid='sources_handler_create_default_document_source',
            receiver=handler_create_default_document_source
        )
        post_version_upload.connect(
            dispatch_uid='sources_handler_copy_transformations_to_version',
            receiver=handler_copy_transformations_to_version
        )
