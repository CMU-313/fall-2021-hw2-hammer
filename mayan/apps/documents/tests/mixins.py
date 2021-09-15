from __future__ import unicode_literals

import os

from django.conf import settings

from mayan.apps.converter.classes import Layer
from mayan.apps.converter.layers import layer_saved_transformations

from ..literals import PAGE_RANGE_ALL
from ..models import DocumentType

from .literals import (
    TEST_DOCUMENT_TYPE_DELETE_PERIOD, TEST_DOCUMENT_TYPE_DELETE_TIME_UNIT,
    TEST_DOCUMENT_TYPE_LABEL, TEST_DOCUMENT_TYPE_LABEL_EDITED,
    TEST_DOCUMENT_TYPE_QUICK_LABEL, TEST_DOCUMENT_TYPE_QUICK_LABEL_EDITED,
    TEST_SMALL_DOCUMENT_FILENAME, TEST_SMALL_DOCUMENT_PATH,
    TEST_TRANSFORMATION_ARGUMENT, TEST_TRANSFORMATION_CLASS,
    TEST_VERSION_COMMENT
)

__all__ = ('DocumentTestMixin',)


class DocumentTestMixin(object):
    auto_create_test_document_type = True
    auto_upload_document = True
    test_document_filename = TEST_SMALL_DOCUMENT_FILENAME
    test_document_path = None

    def setUp(self):
        super(DocumentTestMixin, self).setUp()
        Layer.invalidate_cache()

        self.test_documents = []

        if self.auto_create_test_document_type:
            self._create_test_document_type()

            if self.auto_upload_document:
                self.upload_document()

    def tearDown(self):
        for document_type in DocumentType.objects.all():
            document_type.delete()
        super(DocumentTestMixin, self).tearDown()

    def _create_test_document_type(self):
        self.test_document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE_LABEL
        )

    def _calculate_test_document_path(self):
        if not self.test_document_path:
            self.test_document_path = os.path.join(
                settings.BASE_DIR, 'apps', 'documents', 'tests', 'contrib',
                'sample_documents', self.test_document_filename
            )

    def upload_document(self, label=None):
        self._calculate_test_document_path()

        if not label:
            label = self.test_document_filename

        with open(self.test_document_path, mode='rb') as file_object:
            document = self.test_document_type.new_document(
                file_object=file_object, label=label
            )

        self.test_document = document
        self.test_documents.append(document)
        self.test_document_page = document.latest_version.pages.first()
        self.test_document_version = document.latest_version


class DocumentTypeViewTestMixin(object):
    def _request_test_document_type_create_view(self):
        return self.post(
            viewname='documents:document_type_create',
            data={
                'label': TEST_DOCUMENT_TYPE_LABEL,
                'delete_time_period': TEST_DOCUMENT_TYPE_DELETE_PERIOD,
                'delete_time_unit': TEST_DOCUMENT_TYPE_DELETE_TIME_UNIT
            }
        )

    def _request_test_document_type_delete_view(self):
        return self.post(
            viewname='documents:document_type_delete',
            kwargs={'pk': self.test_document_type.pk}
        )

    def _request_test_document_type_edit_view(self):
        return self.post(
            viewname='documents:document_type_edit',
            kwargs={'pk': self.test_document_type.pk},
            data={
                'label': TEST_DOCUMENT_TYPE_LABEL_EDITED,
            }
        )

    def _request_test_document_type_list_view(self):
        return self.get(viewname='documents:document_type_list')


class DocumentTypeQuickLabelViewTestMixin(object):
    def _request_quick_label_create(self):
        return self.post(
            viewname='documents:document_type_filename_create',
            kwargs={'pk': self.test_document_type.pk},
            data={
                'filename': TEST_DOCUMENT_TYPE_QUICK_LABEL,
            }
        )

    def _request_quick_label_delete(self):
        return self.post(
            viewname='documents:document_type_filename_delete',
            kwargs={'pk': self.test_document_type_filename.pk}
        )

    def _request_quick_label_edit(self):
        return self.post(
            viewname='documents:document_type_filename_edit',
            kwargs={'pk': self.test_document_type_filename.pk},
            data={
                'filename': TEST_DOCUMENT_TYPE_QUICK_LABEL_EDITED,
            }
        )

    def _request_quick_label_list_view(self):
        return self.get(
            viewname='documents:document_type_filename_list',
            kwargs={'pk': self.test_document_type.pk}
        )


class DocumentTypeQuickLabelTestMixin(object):
    def _create_test_quick_label(self):
        self.test_document_type_filename = self.test_document_type.filenames.create(
            filename=TEST_DOCUMENT_TYPE_QUICK_LABEL
        )


class DocumentVersionTestMixin(object):
    def _upload_new_version(self):
        with open(TEST_SMALL_DOCUMENT_PATH, mode='rb') as file_object:
            self.test_document.new_version(
                comment=TEST_VERSION_COMMENT, file_object=file_object
            )


class DocumentVersionViewTestMixin(object):
    def _request_document_version_list_view(self):
        return self.get(
            viewname='documents:document_version_list',
            kwargs={'pk': self.test_document.pk}
        )

    def _request_document_version_revert_view(self, document_version):
        return self.post(
            viewname='documents:document_version_revert',
            kwargs={'pk': document_version.pk}
        )


class DocumentViewTestMixin(object):
    def _create_document_transformation(self):
        layer_saved_transformations.add_transformation_to(
            obj=self.test_document.pages.first(),
            transformation_class=TEST_TRANSFORMATION_CLASS,
            arguments=TEST_TRANSFORMATION_ARGUMENT
        )

    def _request_document_properties_view(self):
        return self.get(
            viewname='documents:document_properties',
            kwargs={'pk': self.test_document.pk}
        )

    def _request_document_properties_edit_get_view(self):
        return self.get(
            viewname='documents:document_edit',
            kwargs={'pk': self.test_document.pk}
        )

    def _request_test_document_list_view(self):
        return self.get(viewname='documents:document_list')

    def _request_test_document_preview_view(self):
        return self.get(
            viewname='documents:document_preview', kwargs={
                'pk': self.test_document.pk
            }
        )

    def _request_test_document_type_edit_get_view(self):
        return self.get(
            viewname='documents:document_document_type_edit',
            kwargs={'pk': self.test_document.pk}
        )

    def _request_test_document_type_edit_post_view(self, document_type):
        return self.post(
            viewname='documents:document_document_type_edit',
            kwargs={'pk': self.test_document.pk},
            data={'document_type': document_type.pk}
        )

    def _request_multiple_document_type_edit(self, document_type):
        return self.post(
            viewname='documents:document_multiple_document_type_edit',
            data={
                'id_list': self.test_document.pk,
                'document_type': document_type.pk
            }
        )

    def _request_document_download_form_get_view(self):
        return self.get(
            viewname='documents:document_download_form', kwargs={
                'pk': self.test_document.pk
            }
        )

    def _request_document_download_form_post_view(self):
        return self.post(
            viewname='documents:document_download_form', kwargs={
                'pk': self.test_document.pk
            }
        )

    def _request_document_download_view(self):
        return self.get(
            viewname='documents:document_download', kwargs={
                'pk': self.test_document.pk
            }
        )

    def _request_document_multiple_download_view(self):
        return self.get(
            viewname='documents:document_multiple_download',
            data={'id_list': self.test_document.pk}
        )

    def _request_document_version_download(self, data=None):
        data = data or {}
        return self.get(
            viewname='documents:document_version_download', kwargs={
                'pk': self.test_document.latest_version.pk
            }, data=data
        )

    def _request_document_update_page_count_view(self):
        return self.post(
            viewname='documents:document_update_page_count',
            kwargs={'pk': self.test_document.pk}
        )

    def _request_document_multiple_update_page_count_view(self):
        return self.post(
            viewname='documents:document_multiple_update_page_count',
            data={'id_list': self.test_document.pk}
        )

    def _request_document_clear_transformations_view(self):
        return self.post(
            viewname='documents:document_clear_transformations',
            kwargs={'pk': self.test_document.pk}
        )

    def _request_document_multiple_clear_transformations(self):
        return self.post(
            viewname='documents:document_multiple_clear_transformations',
            data={'id_list': self.test_document.pk}
        )

    def _request_document_print_view(self):
        return self.get(
            viewname='documents:document_print', kwargs={
                'pk': self.test_document.pk,
            }, data={
                'page_group': PAGE_RANGE_ALL
            }
        )

    def _request_empty_trash_view(self):
        return self.post(viewname='documents:trash_can_empty')


class TrashedDocumentViewTestMixin(object):
    def _request_document_trash_get_view(self):
        return self.get(
            viewname='documents:document_trash', kwargs={
                'pk': self.test_document.pk
            }
        )

    def _request_document_trash_post_view(self):
        return self.post(
            viewname='documents:document_trash', kwargs={
                'pk': self.test_document.pk
            }
        )

    def _request_trashed_document_restore_get_view(self):
        return self.get(
            viewname='documents:document_restore', kwargs={
                'pk': self.test_document.pk
            }
        )

    def _request_trashed_document_restore_post_view(self):
        return self.post(
            viewname='documents:document_restore', kwargs={
                'pk': self.test_document.pk
            }
        )

    def _request_trashed_document_delete_get_view(self):
        return self.get(
            viewname='documents:document_delete', kwargs={
                'pk': self.test_document.pk
            }
        )

    def _request_trashed_document_delete_post_view(self):
        return self.post(
            viewname='documents:document_delete', kwargs={
                'pk': self.test_document.pk
            }
        )

    def _request_trashed_document_list_view(self):
        return self.get(viewname='documents:document_list_deleted')
