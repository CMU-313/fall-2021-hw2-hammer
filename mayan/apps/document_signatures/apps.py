from __future__ import unicode_literals

import logging

from django.apps import apps
from django.db.models.signals import post_delete, post_save
from django.utils.translation import ugettext_lazy as _

from kombu import Exchange, Queue

from mayan.apps.acls import ModelPermission
from mayan.apps.common import (
    MayanAppConfig, menu_facet, menu_object, menu_sidebar, menu_tools
)
from mayan.apps.navigation import SourceColumn
from mayan.celery import app

from .handlers import (
    handler_unverify_key_signatures, handler_verify_key_signatures
)
from .links import (
    link_all_document_version_signature_verify, link_document_signature_list,
    link_document_version_signature_delete,
    link_document_version_signature_detached_create,
    link_document_version_signature_details,
    link_document_version_signature_download,
    link_document_version_signature_embedded_create,
    link_document_version_signature_list,
    link_document_version_signature_upload
)
from .permissions import (
    permission_document_version_sign_detached,
    permission_document_version_sign_embedded,
    permission_document_version_signature_delete,
    permission_document_version_signature_download,
    permission_document_version_signature_upload,
    permission_document_version_signature_view
)
from .queues import *  # NOQA

logger = logging.getLogger(__name__)


class DocumentSignaturesApp(MayanAppConfig):
    app_namespace = 'signatures'
    app_url = 'signatures'
    has_tests = True
    name = 'mayan.apps.document_signatures'
    verbose_name = _('Document signatures')

    def ready(self):
        super(DocumentSignaturesApp, self).ready()

        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )

        DocumentVersion = apps.get_model(
            app_label='documents', model_name='DocumentVersion'
        )

        Key = apps.get_model(
            app_label='django_gpg', model_name='Key'
        )

        EmbeddedSignature = self.get_model('EmbeddedSignature')

        SignatureBaseModel = self.get_model('SignatureBaseModel')

        DocumentVersion.register_post_save_hook(
            order=1, func=EmbeddedSignature.objects.create
        )
        DocumentVersion.register_pre_open_hook(
            order=1, func=EmbeddedSignature.objects.open_signed
        )

        ModelPermission.register(
            model=Document, permissions=(
                permission_document_version_sign_detached,
                permission_document_version_sign_embedded,
                permission_document_version_signature_delete,
                permission_document_version_signature_download,
                permission_document_version_signature_view,
                permission_document_version_signature_upload,
            )
        )

        SourceColumn(
            source=SignatureBaseModel, label=_('Date'), attribute='date'
        )
        SourceColumn(
            source=SignatureBaseModel, label=_('Key ID'),
            attribute='get_key_id'
        )
        SourceColumn(
            source=SignatureBaseModel, label=_('Signature ID'),
            func=lambda context: context['object'].signature_id or _('None')
        )
        SourceColumn(
            source=SignatureBaseModel, label=_('Type'),
            func=lambda context: SignatureBaseModel.objects.get_subclass(
                pk=context['object'].pk
            ).get_signature_type_display()
        )

        app.conf.task_queues.append(
            Queue(
                'signatures', Exchange('signatures'), routing_key='signatures'
            ),
        )

        app.conf.task_routes.update(
            {
                'mayan.apps.document_signatures.tasks.task_verify_key_signatures': {
                    'queue': 'signatures'
                },
                'mayan.apps.document_signatures.tasks.task_unverify_key_signatures': {
                    'queue': 'signatures'
                },
                'mayan.apps.document_signatures.tasks.task_verify_document_version': {
                    'queue': 'signatures'
                },
                'mayan.apps.document_signatures.tasks.task_verify_missing_embedded_signature': {
                    'queue': 'tools'
                },
            }
        )

        menu_facet.bind_links(
            links=(link_document_signature_list,), sources=(Document,)
        )
        menu_facet.bind_links(
            links=(
                link_document_version_signature_list,
            ), position=9, sources=(DocumentVersion,)
        )

        menu_object.bind_links(
            links=(
                link_document_version_signature_detached_create,
                link_document_version_signature_embedded_create
            ), sources=(DocumentVersion,)
        )
        menu_object.bind_links(
            links=(
                link_document_version_signature_details,
                link_document_version_signature_download,
                link_document_version_signature_delete,
            ), sources=(SignatureBaseModel,)
        )
        menu_sidebar.bind_links(
            links=(
                link_document_version_signature_upload,
            ), sources=(DocumentVersion,)
        )
        menu_tools.bind_links(
            links=(link_all_document_version_signature_verify,)
        )

        post_delete.connect(
            dispatch_uid='document_signatures_handler_unverify_key_signatures',
            receiver=handler_unverify_key_signatures, sender=Key
        )
        post_save.connect(
            dispatch_uid='document_signatures_handler_verify_key_signatures',
            receiver=handler_verify_key_signatures, sender=Key
        )
