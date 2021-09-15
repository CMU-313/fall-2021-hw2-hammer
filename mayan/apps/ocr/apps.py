from __future__ import unicode_literals

import logging

from kombu import Exchange, Queue

from django.apps import apps
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls import ModelPermission
from mayan.apps.common import (
    MayanAppConfig, menu_facet, menu_list_facet, menu_multi_item, menu_object,
    menu_secondary, menu_tools
)
from mayan.apps.common.classes import ModelAttribute, ModelField
from mayan.apps.documents.search import document_search, document_page_search
from mayan.apps.documents.signals import post_version_upload
from mayan.apps.navigation import SourceColumn
from mayan.apps.rest_api.fields import HyperlinkField
from mayan.apps.rest_api.serializers import LazyExtraFieldsSerializerMixin
from mayan.celery import app

from .handlers import (
    handler_index_document, handler_initialize_new_ocr_settings,
    handler_ocr_document_version,
)
from .links import (
    link_document_page_ocr_content, link_document_ocr_content,
    link_document_ocr_download, link_document_ocr_errors_list,
    link_document_submit, link_document_multiple_submit,
    link_document_type_ocr_settings, link_document_type_submit,
    link_entry_list
)
from .methods import (
    method_document_get_ocr_content, method_document_page_get_ocr_content,
    method_document_ocr_submit, method_document_version_get_ocr_content,
    method_document_version_ocr_submit
)
from .permissions import (
    permission_document_type_ocr_setup, permission_ocr_document,
    permission_ocr_content_view
)
from .queues import *  # NOQA
from .signals import post_document_version_ocr

logger = logging.getLogger(__name__)


class OCRApp(MayanAppConfig):
    app_namespace = 'ocr'
    app_url = 'ocr'
    has_rest_api = True
    has_tests = True
    name = 'mayan.apps.ocr'
    verbose_name = _('OCR')

    def ready(self):
        super(OCRApp, self).ready()

        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )
        DocumentPage = apps.get_model(
            app_label='documents', model_name='DocumentPage'
        )
        DocumentType = apps.get_model(
            app_label='documents', model_name='DocumentType'
        )
        DocumentTypeSettings = self.get_model(
            model_name='DocumentTypeSettings'
        )
        DocumentVersion = apps.get_model(
            app_label='documents', model_name='DocumentVersion'
        )

        DocumentVersionOCRError = self.get_model('DocumentVersionOCRError')

        Document.add_to_class(
            name='get_ocr_content',
            value=method_document_get_ocr_content
        )
        Document.add_to_class(
            name='submit_for_ocr', value=method_document_ocr_submit
        )
        DocumentPage.add_to_class(
            name='get_ocr_content', value=method_document_page_get_ocr_content
        )
        DocumentVersion.add_to_class(
            name='get_ocr_content',
            value=method_document_version_get_ocr_content
        )
        DocumentVersion.add_to_class(
            name='submit_for_ocr', value=method_document_version_ocr_submit
        )

        LazyExtraFieldsSerializerMixin.add_field(
            dotted_path='mayan.apps.documents.serializers.DocumentPageSerializer',
            field_name='ocr_content_url',
            field=HyperlinkField(
                view_kwargs=(
                    {
                        'lookup_field': 'document_version__document_id',
                        'lookup_url_kwarg': 'document_id',
                    },
                    {
                        'lookup_field': 'document_version_id',
                        'lookup_url_kwarg': 'document_version_id',
                    },
                    {
                        'lookup_field': 'pk',
                        'lookup_url_kwarg': 'document_page_id',
                    }
                ),
                view_name='rest_api:document_page-ocr-content'
            )
        )

        LazyExtraFieldsSerializerMixin.add_field(
            dotted_path='mayan.apps.documents.serializers.DocumentSerializer',
            field_name='ocr_content_url',
            field=HyperlinkField(
                lookup_url_kwarg='document_id',
                view_name='rest_api:document-ocr-content'
            )
        )

        LazyExtraFieldsSerializerMixin.add_field(
            dotted_path='mayan.apps.documents.serializers.DocumentSerializer',
            field_name='ocr_submit_url',
            field=HyperlinkField(
                lookup_url_kwarg='document_id',
                view_name='rest_api:document-ocr-submit'
            )
        )

        LazyExtraFieldsSerializerMixin.add_field(
            dotted_path='mayan.apps.documents.serializers.DocumentVersionSerializer',
            field_name='ocr_submit_url',
            field=HyperlinkField(
                view_kwargs=(
                    {
                        'lookup_field': 'document_id',
                        'lookup_url_kwarg': 'document_id',
                    },
                    {
                        'lookup_field': 'pk',
                        'lookup_url_kwarg': 'document_version_id',
                    }
                ),
                view_name='rest_api:document_version-ocr-submit'
            )
        )

        LazyExtraFieldsSerializerMixin.add_field(
            dotted_path='mayan.apps.documents.serializers.DocumentVersionSerializer',
            field_name='ocr_content_url',
            field=HyperlinkField(
                view_kwargs=(
                    {
                        'lookup_field': 'document_id',
                        'lookup_url_kwarg': 'document_id',
                    },
                    {
                        'lookup_field': 'pk',
                        'lookup_url_kwarg': 'document_version_id',
                    }
                ),
                view_name='rest_api:document_version-ocr-content'
            )
        )

        ModelAttribute(model=Document, name='get_ocr_content')

        ModelField(
            model=Document, name='versions__pages__ocr_content__content'
        )

        ModelPermission.register(
            model=Document, permissions=(
                permission_ocr_document, permission_ocr_content_view
            )
        )
        ModelPermission.register(
            model=DocumentType, permissions=(
                permission_document_type_ocr_setup, permission_ocr_document
            )
        )
        ModelPermission.register_inheritance(
            model=DocumentTypeSettings, related='document_type',
        )

        SourceColumn(
            attribute='document_version__document', is_absolute_url=True,
            is_identifier=True, is_sortable=True, source=DocumentVersionOCRError
        )
        SourceColumn(
            attribute='datetime_submitted', is_sortable=True,
            label=_('Date and time'), source=DocumentVersionOCRError
        )
        SourceColumn(
            attribute='result', source=DocumentVersionOCRError
        )

        app.conf.task_queues.append(
            Queue('ocr', Exchange('ocr'), routing_key='ocr'),
        )

        app.conf.task_routes.update(
            {
                'mayan.apps.ocr.tasks.task_do_ocr': {
                    'queue': 'ocr'
                },
            }
        )

        document_search.add_model_field(
            field='versions__pages__ocr_content__content', label=_('OCR')
        )

        document_page_search.add_model_field(
            field='ocr_content__content', label=_('OCR')
        )

        menu_facet.bind_links(
            links=(link_document_ocr_content,), sources=(Document,)
        )
        menu_list_facet.bind_links(
            links=(link_document_page_ocr_content,), sources=(DocumentPage,)
        )
        menu_multi_item.bind_links(
            links=(link_document_multiple_submit,), sources=(Document,)
        )
        menu_object.bind_links(
            links=(link_document_type_ocr_settings,), sources=(DocumentType,)
        )
        menu_secondary.bind_links(
            links=(
                link_document_submit, link_document_ocr_download,
                link_document_ocr_errors_list
            ),
            sources=(
                'ocr:document_content', 'ocr:document_error_list',
                'ocr:document_download',
            )
        )
        menu_secondary.bind_links(
            links=(link_entry_list,),
            sources=(
                'ocr:entry_list', 'ocr:entry_delete_multiple',
                'ocr:entry_re_queue_multiple', DocumentVersionOCRError
            )
        )
        menu_tools.bind_links(
            links=(
                link_document_type_submit, link_entry_list
            )
        )

        post_document_version_ocr.connect(
            dispatch_uid='ocr_handler_index_document',
            receiver=handler_index_document,
            sender=DocumentVersion
        )
        post_save.connect(
            dispatch_uid='ocr_handler_initialize_new_ocr_settings',
            receiver=handler_initialize_new_ocr_settings,
            sender=DocumentType
        )
        post_version_upload.connect(
            dispatch_uid='ocr_handler_ocr_document_version',
            receiver=handler_ocr_document_version,
            sender=DocumentVersion
        )
