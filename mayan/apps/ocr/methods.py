from __future__ import unicode_literals

from datetime import timedelta

from django.apps import apps
from django.utils.timezone import now

from mayan.apps.common.settings import settings_db_sync_task_delay

from .events import event_ocr_document_version_submit
from .tasks import task_do_ocr


def method_document_ocr_submit(self):
    latest_version = self.latest_version
    # Don't error out if document has no version
    if latest_version:
        latest_version.submit_for_ocr()


def method_document_page_get_ocr_content(self):
    DocumentVersionPageOCRContent = apps.get_model(
        app_label='ocr', model_name='DocumentVersionPageOCRContent'
    )

    try:
        return self.content_object.ocr_content.content
    except (AttributeError, DocumentVersionPageOCRContent.DoesNotExist):
        return None


def method_document_version_ocr_submit(self):
    event_ocr_document_version_submit.commit(
        action_object=self.document, target=self
    )

    task_do_ocr.apply_async(
        eta=now() + timedelta(seconds=settings_db_sync_task_delay.value),
        kwargs={'document_version_pk': self.pk},
    )
