from __future__ import unicode_literals

import logging

from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import OperationalError

from mayan.celery import app

from .literals import (
    UPDATE_PAGE_COUNT_RETRY_DELAY, UPLOAD_NEW_DOCUMENT_RETRY_DELAY,
    UPLOAD_NEW_VERSION_RETRY_DELAY
)

logger = logging.getLogger(__name__)


@app.task(ignore_result=True)
def task_clean_empty_duplicate_lists():
    DuplicatedDocument = apps.get_model(
        app_label='documents', model_name='DuplicatedDocument'
    )
    DuplicatedDocument.objects.clean_empty_duplicate_lists()


@app.task(ignore_result=True)
def task_check_delete_periods():
    DocumentType = apps.get_model(
        app_label='documents', model_name='DocumentType'
    )

    DocumentType.objects.check_delete_periods()


@app.task(ignore_result=True)
def task_check_trash_periods():
    DocumentType = apps.get_model(
        app_label='documents', model_name='DocumentType'
    )

    DocumentType.objects.check_trash_periods()


@app.task(ignore_result=True)
def task_delete_document(trashed_document_id):
    DeletedDocument = apps.get_model(
        app_label='documents', model_name='DeletedDocument'
    )

    logger.debug(msg='Executing')
    deleted_document = DeletedDocument.objects.get(pk=trashed_document_id)
    deleted_document.delete()
    logger.debug(msg='Finshed')


@app.task(ignore_result=True)
def task_delete_stubs():
    Document = apps.get_model(
        app_label='documents', model_name='Document'
    )

    logger.info(msg='Executing')
    Document.passthrough.delete_stubs()
    logger.info(msg='Finshed')


@app.task()
def task_generate_document_page_image(document_page_id, *args, **kwargs):
    DocumentPage = apps.get_model(
        app_label='documents', model_name='DocumentPage'
    )

    document_page = DocumentPage.passthrough.get(pk=document_page_id)
    return document_page.generate_image(*args, **kwargs)


@app.task(ignore_result=True)
def task_scan_duplicates_all():
    DuplicatedDocument = apps.get_model(
        app_label='documents', model_name='DuplicatedDocument'
    )

    DuplicatedDocument.objects.scan()


@app.task(ignore_result=True)
def task_scan_duplicates_for(document_id):
    Document = apps.get_model(
        app_label='documents', model_name='Document'
    )
    DuplicatedDocument = apps.get_model(
        app_label='documents', model_name='DuplicatedDocument'
    )

    document = Document.objects.get(pk=document_id)

    DuplicatedDocument.objects.scan_for(document=document)


@app.task(bind=True, default_retry_delay=UPDATE_PAGE_COUNT_RETRY_DELAY, ignore_result=True)
def task_update_page_count(self, version_id):
    DocumentVersion = apps.get_model(
        app_label='documents', model_name='DocumentVersion'
    )

    document_version = DocumentVersion.objects.get(pk=version_id)
    try:
        document_version.update_page_count()
    except OperationalError as exception:
        logger.warning(
            'Operational error during attempt to update page count for '
            'document version: %s; %s. Retrying.', document_version,
            exception
        )
        raise self.retry(exc=exception)


@app.task(bind=True, default_retry_delay=UPLOAD_NEW_DOCUMENT_RETRY_DELAY, ignore_result=True)
def task_upload_new_document(self, document_type_id, shared_uploaded_file_id):
    DocumentType = apps.get_model(
        app_label='documents', model_name='DocumentType'
    )

    SharedUploadedFile = apps.get_model(
        app_label='common', model_name='SharedUploadedFile'
    )

    try:
        document_type = DocumentType.objects.get(pk=document_type_id)
        shared_file = SharedUploadedFile.objects.get(
            pk=shared_uploaded_file_id
        )
    except OperationalError as exception:
        logger.warning(
            'Operational error during attempt to retrieve shared data for '
            'new document of type: %s; %s. Retrying.', document_type, exception
        )
        raise self.retry(exc=exception)

    try:
        with shared_file.open() as file_object:
            document_type.new_document(file_object=file_object)
    except OperationalError as exception:
        logger.warning(
            'Operational error during attempt to create new document '
            'of type: %s; %s. Retrying.', document_type, exception
        )
        raise self.retry(exc=exception)
    except Exception as exception:
        # This except and else block emulate a finally:
        logger.error(
            'Unexpected error during attempt to create new document '
            'of type: %s; %s', document_type, exception
        )
        try:
            shared_file.delete()
        except OperationalError as exception:
            logger.warning(
                'Operational error during attempt to delete shared '
                'file: %s; %s.', shared_file, exception
            )
    else:
        try:
            shared_file.delete()
        except OperationalError as exception:
            logger.warning(
                'Operational error during attempt to delete shared '
                'file: %s; %s.', shared_file, exception
            )


@app.task(bind=True, default_retry_delay=UPLOAD_NEW_VERSION_RETRY_DELAY, ignore_result=True)
def task_upload_new_version(self, document_id, shared_uploaded_file_id, user_id, comment=None):
    SharedUploadedFile = apps.get_model(
        app_label='common', model_name='SharedUploadedFile'
    )

    Document = apps.get_model(
        app_label='documents', model_name='Document'
    )

    DocumentVersion = apps.get_model(
        app_label='documents', model_name='DocumentVersion'
    )

    try:
        document = Document.passthrough.get(pk=document_id)
        shared_file = SharedUploadedFile.objects.get(
            pk=shared_uploaded_file_id
        )
        if user_id:
            user = get_user_model().objects.get(pk=user_id)
        else:
            user = None

    except OperationalError as exception:
        logger.warning(
            'Operational error during attempt to retrieve shared data for '
            'new document version for:%s; %s. Retrying.', document, exception
        )
        raise self.retry(exc=exception)

    with shared_file.open() as file_object:
        document_version = DocumentVersion(
            document=document, comment=comment or '', file=file_object
        )
        try:
            document_version.save(_user=user)
        except Warning as warning:
            # New document version are blocked
            logger.info(
                'Warning during attempt to create new document version for '
                'document: %s; %s', document, warning
            )
            shared_file.delete()
        except OperationalError as exception:
            logger.warning(
                'Operational error during attempt to create new document '
                'version for document: %s; %s. Retrying.', document, exception
            )
            raise self.retry(exc=exception)
        except Exception as exception:
            # This except and else block emulate a finally:
            logger.error(
                'Unexpected error during attempt to create new document '
                'version for document: %s; %s', document, exception
            )
            try:
                shared_file.delete()
            except OperationalError as exception:
                logger.warning(
                    'Operational error during attempt to delete shared '
                    'file: %s; %s.', shared_file, exception
                )
        else:
            try:
                shared_file.delete()
            except OperationalError as exception:
                logger.warning(
                    'Operational error during attempt to delete shared '
                    'file: %s; %s.', shared_file, exception
                )
