from __future__ import absolute_import, unicode_literals

from datetime import timedelta

from django.db.models.signals import post_delete, post_migrate
from django.utils.translation import ugettext_lazy as _

from kombu import Exchange, Queue

from mayan.apps.acls import ModelPermission
from mayan.apps.acls.links import link_acl_list
from mayan.apps.acls.permissions import (
    permission_acl_edit, permission_acl_view
)
from mayan.apps.common import (
    MayanAppConfig, MissingItem, menu_facet, menu_list_facet, menu_main,
    menu_multi_item, menu_object, menu_secondary, menu_setup, menu_tools
)
from mayan.apps.common.classes import ModelField, Template
from mayan.apps.common.signals import post_initial_setup
from mayan.apps.common.widgets import TwoStateWidget
from mayan.apps.converter.links import link_transformation_list
from mayan.apps.converter.permissions import (
    permission_transformation_create, permission_transformation_delete,
    permission_transformation_edit, permission_transformation_view
)
from mayan.apps.dashboards.dashboards import dashboard_main
from mayan.apps.events import ModelEventType
from mayan.apps.events.links import (
    link_events_for_object, link_object_event_types_user_subcriptions_list
)
from mayan.apps.events.permissions import permission_events_view
from mayan.apps.navigation import SourceColumn
from mayan.apps.rest_api.fields import DynamicSerializerField
from mayan.celery import app

from .dashboard_widgets import (
    DashboardWidgetDocumentPagesTotal, DashboardWidgetDocumentsInTrash,
    DashboardWidgetDocumentsNewThisMonth,
    DashboardWidgetDocumentsPagesNewThisMonth, DashboardWidgetDocumentsTotal,
    DashboardWidgetDocumentsTypesTotal
)
from .events import (
    event_document_create, event_document_download, event_document_new_version,
    event_document_properties_edit, event_document_type_change,
    event_document_type_created, event_document_type_edited,
    event_document_version_revert, event_document_view
)
from .handlers import (
    handler_create_default_document_type, handler_create_document_cache,
    handler_remove_empty_duplicates_lists, handler_scan_duplicates_for
)
from .links import (
    link_clear_image_cache, link_trashed_document_delete,
    link_document_change_type, link_document_download,
    link_document_duplicates_list, link_document_edit,
    link_document_favorites_add, link_document_favorites_remove,
    link_document_list, link_trashed_document_list,
    link_document_list_favorites, link_document_list_recent_access,
    link_document_list_recent_added,
    link_document_multiple_change_type,
    link_document_multiple_download, link_document_multiple_favorites_add,
    link_document_multiple_favorites_remove, link_trashed_document_multiple_restore,
    link_document_multiple_trash,
    link_document_multiple_transformations_clear,
    link_document_multiple_update_page_count,
    link_document_page_navigation_first, link_document_page_navigation_last,
    link_document_page_navigation_next, link_document_page_navigation_previous,
    link_document_page_return, link_document_page_rotate_left,
    link_document_page_rotate_right, link_document_page_view,
    link_document_page_view_reset, link_document_page_zoom_in,
    link_document_page_zoom_out, link_document_pages, link_document_preview,
    link_document_print, link_document_properties,
    link_document_quick_download, link_trashed_document_restore, link_document_trash,
    link_document_type_create, link_document_type_delete,
    link_document_type_edit, link_document_type_filename_create,
    link_document_type_filename_delete, link_document_type_filename_edit,
    link_document_type_filename_list, link_document_type_list,
    link_document_type_setup, link_document_update_page_count,
    link_document_version_download, link_document_version_list,
    link_document_version_return_document, link_document_version_return_list,
    link_document_version_revert, link_document_version_view,
    link_duplicated_document_list, link_duplicated_document_scan,
    link_document_transformations_clear, link_document_transformations_clone,
    link_trash_can_empty, link_trashed_document_multiple_delete
)
from .literals import (
    CHECK_DELETE_PERIOD_INTERVAL, CHECK_TRASH_PERIOD_INTERVAL,
    DELETE_STALE_STUBS_INTERVAL
)
from .menus import menu_documents
from .permissions import (
    permission_document_create,
    permission_document_download, permission_document_edit,
    permission_document_new_version, permission_document_print,
    permission_document_properties_edit, permission_document_trash,
    permission_document_type_delete, permission_document_type_edit,
    permission_document_type_view, permission_document_version_revert,
    permission_document_version_view, permission_document_view,
    permission_trashed_document_delete, permission_trashed_document_restore
)
from .queues import *  # NOQA
# Just import to initialize the search models
from .search import document_page_search, document_search  # NOQA
from .signals import post_version_upload
from .statistics import *  # NOQA
from .widgets import DocumentPageThumbnailWidget


class DocumentsApp(MayanAppConfig):
    app_namespace = 'documents'
    app_url = 'documents'
    has_rest_api = True
    has_tests = True
    name = 'mayan.apps.documents'
    verbose_name = _('Documents')

    def ready(self):
        super(DocumentsApp, self).ready()
        from actstream import registry

        Document = self.get_model(model_name='Document')
        DocumentPage = self.get_model(model_name='DocumentPage')
        DocumentPageSearchResult = self.get_model(
            model_name='DocumentPageSearchResult'
        )
        DocumentType = self.get_model(model_name='DocumentType')
        DocumentTypeFilename = self.get_model(model_name='DocumentTypeFilename')
        DocumentVersion = self.get_model(model_name='DocumentVersion')
        DuplicatedDocumentProxy = self.get_model(
            model_name='DuplicatedDocumentProxy'
        )
        TrashedDocument = self.get_model(model_name='TrashedDocument')

        DynamicSerializerField.add_serializer(
            klass=Document,
            serializer_class='mayan.apps.documents.serializers.DocumentSerializer'
        )

        MissingItem(
            label=_('Create a document type'),
            description=_(
                'Every uploaded document must be assigned a document type, '
                'it is the basic way Mayan EDMS categorizes documents.'
            ), condition=lambda: not DocumentType.objects.exists(),
            view='documents:document_type_list'
        )

        ModelField(Document, name='description')
        ModelField(Document, name='date_added')
        ModelField(Document, name='deleted_date_time')
        ModelField(Document, name='document_type__label')
        ModelField(Document, name='in_trash')
        ModelField(Document, name='is_stub')
        ModelField(Document, name='label')
        ModelField(Document, name='language')
        ModelField(Document, name='uuid')
        ModelField(
            Document, name='versions__checksum'
        )
        ModelField(
            Document, label=_('Versions comment'), name='versions__comment'
        )
        ModelField(
            Document, label=_('Versions encoding'), name='versions__encoding'
        )
        ModelField(
            Document, label=_('Versions mime type'), name='versions__mimetype'
        )
        ModelField(
            Document, label=_('Versions timestamp'), name='versions__timestamp'
        )

        ModelEventType.register(
            model=DocumentType, event_types=(
                event_document_create,
                event_document_type_created,
                event_document_type_edited,
            )
        )
        ModelEventType.register(
            model=Document, event_types=(
                event_document_download, event_document_properties_edit,
                event_document_type_change, event_document_new_version,
                event_document_version_revert, event_document_view
            )
        )

        ModelPermission.register(
            model=Document, permissions=(
                permission_acl_edit, permission_acl_view,
                permission_document_download, permission_document_edit,
                permission_document_new_version, permission_document_print,
                permission_document_properties_edit, permission_document_trash,
                permission_document_version_revert,
                permission_document_version_view, permission_document_view,
                permission_events_view, permission_transformation_create,
                permission_transformation_delete,
                permission_transformation_edit, permission_transformation_view,
                permission_trashed_document_delete,
                permission_trashed_document_restore
            )
        )

        ModelPermission.register(
            model=DocumentType, permissions=(
                permission_document_create, permission_document_type_delete,
                permission_document_type_edit, permission_document_type_view
            )
        )

        ModelPermission.register_proxy(
            source=Document, model=DocumentType,
        )

        ModelPermission.register_inheritance(
            model=Document, related='document_type',
        )
        ModelPermission.register_inheritance(
            model=DocumentPage, related='document_version__document',
        )
        ModelPermission.register_inheritance(
            model=DocumentPageSearchResult, related='document_version__document',
        )
        ModelPermission.register_inheritance(
            model=DocumentTypeFilename, related='document_type',
        )
        ModelPermission.register_inheritance(
            model=DocumentVersion, related='document',
        )

        Template(
            name='invalid_document',
            template_name='documents/invalid_document.html'
        )

        # Document and document page thumbnail widget
        document_page_thumbnail_widget = DocumentPageThumbnailWidget()

        # Document
        SourceColumn(
            attribute='label', is_absolute_url=True, is_identifier=True,
            is_sortable=True, source=Document
        )
        SourceColumn(
            func=lambda context: document_page_thumbnail_widget.render(
                instance=context['object']
            ), label=_('Thumbnail'), source=Document
        )
        SourceColumn(
            attribute='document_type', is_sortable=True, label=_('Type'),
            source=Document
        )
        SourceColumn(
            attribute='get_page_count', include_label=True, source=Document
        )
        SourceColumn(
            attribute='date_added', is_sortable=True, source=Document, views=(
                'documents:document_list_recent_added',
            )
        )

        # DocumentPage
        SourceColumn(
            attribute='get_label', is_absolute_url=True, is_identifier=True,
            source=DocumentPage
        )
        SourceColumn(
            func=lambda context: document_page_thumbnail_widget.render(
                instance=context['object']
            ), label=_('Thumbnail'), source=DocumentPage
        )

        SourceColumn(
            func=lambda context: document_page_thumbnail_widget.render(
                instance=context['object']
            ), label=_('Thumbnail'), source=DocumentPageSearchResult
        )

        SourceColumn(
            attribute='document_version.document.document_type',
            label=_('Type'), source=DocumentPageSearchResult
        )

        # DocumentType
        SourceColumn(
            attribute='label', is_identifier=True, is_sortable=True,
            source=DocumentType
        )
        SourceColumn(
            func=lambda context: context['object'].get_document_count(
                user=context['request'].user
            ), label=_('Documents'), source=DocumentType
        )

        SourceColumn(
            attribute='filename', is_identifier=True, is_sortable=True,
            source=DocumentTypeFilename
        )
        SourceColumn(
            attribute='enabled', is_sortable=True, source=DocumentTypeFilename,
            widget=TwoStateWidget
        )

        # TrashedDocument
        SourceColumn(
            attribute='label', is_identifier=True, is_sortable=True,
            source=TrashedDocument
        )
        SourceColumn(
            func=lambda context: document_page_thumbnail_widget.render(
                instance=context['object']
            ), label=_('Thumbnail'), source=TrashedDocument
        )

        SourceColumn(
            attribute='document_type', is_sortable=True, source=TrashedDocument
        )
        SourceColumn(
            attribute='get_rendered_deleted_date_time', source=TrashedDocument
        )

        # DocumentVersion
        SourceColumn(
            attribute='get_rendered_timestamp', is_identifier=True,
            source=DocumentVersion
        )
        SourceColumn(
            func=lambda context: document_page_thumbnail_widget.render(
                instance=context['object']
            ), label=_('Thumbnail'), source=DocumentVersion
        )
        SourceColumn(attribute='get_page_count', source=DocumentVersion)
        SourceColumn(
            attribute='mimetype', is_sortable=True, source=DocumentVersion
        )
        SourceColumn(
            attribute='encoding', is_sortable=True, source=DocumentVersion
        )
        SourceColumn(
            attribute='comment', is_sortable=True, source=DocumentVersion
        )

        # DuplicatedDocument
        SourceColumn(
            attribute='label', is_absolute_url=True, is_identifier=True,
            is_sortable=True, source=DuplicatedDocumentProxy
        )
        SourceColumn(
            func=lambda context: document_page_thumbnail_widget.render(
                instance=context['object']
            ), label=_('Thumbnail'), source=DuplicatedDocumentProxy
        )
        SourceColumn(
            func=lambda context: context['object'].get_duplicate_count(
                user=context['request'].user
            ), include_label=True, label=_('Duplicates'),
            source=DuplicatedDocumentProxy
        )

        app.conf.beat_schedule.update(
            {
                'task_check_delete_periods': {
                    'task': 'mayan.apps.documents.tasks.task_check_delete_periods',
                    'schedule': timedelta(
                        seconds=CHECK_DELETE_PERIOD_INTERVAL
                    ),
                },
                'task_check_trash_periods': {
                    'task': 'mayan.apps.documents.tasks.task_check_trash_periods',
                    'schedule': timedelta(seconds=CHECK_TRASH_PERIOD_INTERVAL),
                },
                'task_delete_stubs': {
                    'task': 'mayan.apps.documents.tasks.task_delete_stubs',
                    'schedule': timedelta(seconds=DELETE_STALE_STUBS_INTERVAL),
                },
            }
        )

        app.conf.task_queues.extend(
            (
                Queue(
                    'converter', Exchange('converter'),
                    routing_key='converter', delivery_mode=1
                ),
                Queue(
                    'documents_periodic', Exchange('documents_periodic'),
                    routing_key='documents_periodic', delivery_mode=1
                ),
                Queue('uploads', Exchange('uploads'), routing_key='uploads'),
                Queue(
                    'documents', Exchange('documents'), routing_key='documents'
                ),
            )
        )

        app.conf.task_routes.update(
            {
                'mayan.apps.documents.tasks.task_check_delete_periods': {
                    'queue': 'documents_periodic'
                },
                'mayan.apps.documents.tasks.task_check_trash_periods': {
                    'queue': 'documents_periodic'
                },
                'mayan.apps.documents.tasks.task_clean_empty_duplicate_lists': {
                    'queue': 'documents'
                },
                'mayan.apps.documents.tasks.task_clear_image_cache': {
                    'queue': 'tools'
                },
                'mayan.apps.documents.tasks.task_delete_document': {
                    'queue': 'documents'
                },
                'mayan.apps.documents.tasks.task_delete_stubs': {
                    'queue': 'documents_periodic'
                },
                'mayan.apps.documents.tasks.task_generate_document_page_image': {
                    'queue': 'converter'
                },
                'mayan.apps.documents.tasks.task_scan_duplicates_all': {
                    'queue': 'tools'
                },
                'mayan.apps.documents.tasks.task_scan_duplicates_for': {
                    'queue': 'uploads'
                },
                'mayan.apps.documents.tasks.task_update_page_count': {
                    'queue': 'uploads'
                },
                'mayan.apps.documents.tasks.task_upload_new_version': {
                    'queue': 'uploads'
                },
            }
        )

        dashboard_main.add_widget(
            widget=DashboardWidgetDocumentsTotal, order=0
        )
        dashboard_main.add_widget(
            widget=DashboardWidgetDocumentPagesTotal, order=1
        )
        dashboard_main.add_widget(
            widget=DashboardWidgetDocumentsInTrash, order=2
        )
        dashboard_main.add_widget(
            widget=DashboardWidgetDocumentsTypesTotal, order=3
        )
        dashboard_main.add_widget(
            widget=DashboardWidgetDocumentsNewThisMonth, order=4
        )
        dashboard_main.add_widget(
            widget=DashboardWidgetDocumentsPagesNewThisMonth, order=5
        )

        menu_documents.bind_links(
            links=(
                link_document_list_recent_access,
                link_document_list_recent_added, link_document_list_favorites,
                link_document_list, link_trashed_document_list,
                link_duplicated_document_list,
            )
        )

        menu_main.bind_links(links=(menu_documents,), position=0)

        menu_setup.bind_links(links=(link_document_type_setup,))
        menu_tools.bind_links(
            links=(link_clear_image_cache, link_duplicated_document_scan)
        )

        # Document type links
        menu_list_facet.bind_links(
            links=(
                link_document_type_filename_list,
                link_acl_list, link_object_event_types_user_subcriptions_list,
                link_events_for_object,
            ), sources=(DocumentType,)
        )
        menu_object.bind_links(
            links=(
                link_document_type_edit, link_document_type_delete,
            ), sources=(DocumentType,)
        )
        menu_object.bind_links(
            links=(
                link_document_type_filename_edit,
                link_document_type_filename_delete
            ), sources=(DocumentTypeFilename,)
        )
        menu_secondary.bind_links(
            links=(link_document_type_list, link_document_type_create),
            sources=(
                DocumentType, 'documents:document_type_create',
                'documents:document_type_list'
            )
        )
        menu_secondary.bind_links(
            links=(link_document_type_filename_create,),
            sources=(
                DocumentTypeFilename, 'documents:document_type_filename_list',
                'documents:document_type_filename_create'
            )
        )
        menu_secondary.bind_links(
            links=(link_trash_can_empty,),
            sources=(
                'documents:trashed_document_list', 'documents:trash_can_empty'
            )
        )

        # Document object links
        menu_object.bind_links(
            links=(
                link_document_favorites_add, link_document_favorites_remove,
                link_document_edit, link_document_change_type,
                link_document_print, link_document_trash,
                link_document_quick_download, link_document_download,
                link_document_transformations_clear,
                link_document_transformations_clone,
                link_document_update_page_count,
            ), sources=(Document,)
        )
        menu_object.bind_links(
            links=(link_trashed_document_restore, link_trashed_document_delete),
            sources=(TrashedDocument,)
        )

        # Document facet links
        menu_facet.bind_links(
            links=(link_document_duplicates_list, link_acl_list,),
            sources=(Document,)
        )
        menu_facet.bind_links(
            links=(link_document_preview,), sources=(Document,), position=0
        )
        menu_facet.bind_links(
            links=(link_document_properties,), sources=(Document,), position=2
        )
        menu_facet.bind_links(
            links=(
                link_events_for_object,
                link_object_event_types_user_subcriptions_list,
                link_document_version_list,
            ), sources=(Document,), position=2
        )
        menu_facet.bind_links(links=(link_document_pages,), sources=(Document,))

        # Document actions
        menu_object.bind_links(
            links=(
                link_document_version_revert, link_document_version_download
            ),
            sources=(DocumentVersion,)
        )
        menu_multi_item.bind_links(
            links=(
                link_document_multiple_favorites_add,
                link_document_multiple_favorites_remove,
                link_document_multiple_transformations_clear,
                link_document_multiple_trash, link_document_multiple_download,
                link_document_multiple_update_page_count,
                link_document_multiple_change_type,
            ), sources=(Document,)
        )
        menu_multi_item.bind_links(
            links=(
                link_trashed_document_multiple_restore,
                link_trashed_document_multiple_delete
            ), sources=(TrashedDocument,)
        )

        # Document pages
        menu_facet.add_unsorted_source(source=DocumentPage)
        menu_facet.bind_links(
            links=(
                link_document_page_rotate_left,
                link_document_page_rotate_right, link_document_page_zoom_in,
                link_document_page_zoom_out, link_document_page_view_reset
            ), sources=('documents:document_page_view',)
        )
        menu_facet.bind_links(
            links=(link_document_page_return, link_document_page_view),
            sources=(DocumentPage,)
        )
        menu_facet.bind_links(
            links=(
                link_document_page_navigation_first,
                link_document_page_navigation_previous,
                link_document_page_navigation_next,
                link_document_page_navigation_last,
            ), sources=(DocumentPage,)
        )
        menu_list_facet.bind_links(
            links=(link_transformation_list,), sources=(DocumentPage,)
        )

        # Document versions
        menu_facet.bind_links(
            links=(
                link_document_version_return_document,
                link_document_version_return_list
            ), sources=(DocumentVersion,)
        )
        menu_facet.bind_links(
            links=(link_document_version_view,), sources=(DocumentVersion,)
        )
        menu_object.bind_links(
            links=(link_document_version_view,), sources=(DocumentVersion,)
        )

        post_delete.connect(
            dispatch_uid='documents_handler_remove_empty_duplicates_lists',
            receiver=handler_remove_empty_duplicates_lists,
            sender=Document,
        )
        post_initial_setup.connect(
            dispatch_uid='documents_handler_create_default_document_type',
            receiver=handler_create_default_document_type,
        )
        post_migrate.connect(
            dispatch_uid='documents_handler_create_document_cache',
            receiver=handler_create_document_cache,
        )
        post_version_upload.connect(
            dispatch_uid='documents_handler_scan_duplicates_for',
            receiver=handler_scan_duplicates_for,
        )

        registry.register(TrashedDocument)
        registry.register(Document)
        registry.register(DocumentType)
        registry.register(DocumentVersion)
