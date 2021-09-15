from __future__ import unicode_literals

import logging
import os
import shutil

from mayan.apps.checkouts.models import NewVersionBlock
from mayan.apps.common.tests import GenericViewTestCase
from mayan.apps.common.utils import fs_cleanup, mkdtemp
from mayan.apps.documents.models import Document
from mayan.apps.documents.permissions import permission_document_create
from mayan.apps.documents.tests import (
    TEST_DOCUMENT_DESCRIPTION, TEST_SMALL_DOCUMENT_CHECKSUM,
    TEST_SMALL_DOCUMENT_PATH, GenericDocumentViewTestCase
)

from ..links import link_upload_version
from ..literals import SOURCE_CHOICE_WEB_FORM
from ..models import StagingFolderSource, WebFormSource
from ..permissions import (
    permission_sources_setup_create, permission_sources_setup_delete,
    permission_sources_setup_view, permission_staging_file_delete
)

from .literals import (
    TEST_SOURCE_LABEL, TEST_SOURCE_UNCOMPRESS_N, TEST_STAGING_PREVIEW_WIDTH
)


class DocumentUploadTestCase(GenericDocumentViewTestCase):
    auto_upload_document = False

    def setUp(self):
        super(DocumentUploadTestCase, self).setUp()
        self._create_source()
        self.login_user()

    def _create_source(self):
        self.source = WebFormSource.objects.create(
            enabled=True, label=TEST_SOURCE_LABEL,
            uncompress=TEST_SOURCE_UNCOMPRESS_N
        )

    def _request_upload_wizard_view(self):
        logging.getLogger('django.request').setLevel(level=logging.CRITICAL)

        with open(TEST_SMALL_DOCUMENT_PATH, mode='rb') as file_object:
            return self.post(
                viewname='sources:upload_interactive', args=(self.source.pk,),
                data={
                    'source-file': file_object,
                    'document_type_id': self.document_type.pk,
                }, follow=True
            )

    def test_upload_wizard_without_permission(self):
        response = self._request_upload_wizard_view()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Document.objects.count(), 0)

    def test_upload_wizard_with_permission(self):
        self.grant_permission(permission=permission_document_create)

        response = self._request_upload_wizard_view()

        self.assertTrue(b'queued' in response.content)
        self.assertEqual(Document.objects.count(), 1)
        self.assertEqual(
            Document.objects.first().checksum, TEST_SMALL_DOCUMENT_CHECKSUM
        )

    def test_upload_wizard_with_document_type_access(self):
        """
        Test uploading of documents by granting the document create
        permssion for the document type to the user
        """
        # Create an access control entry giving the role the document
        # create permission for the selected document type.
        self.grant_access(
            obj=self.document_type, permission=permission_document_create
        )

        response = self._request_upload_wizard_view()

        self.assertTrue(b'queued' in response.content)
        self.assertEqual(Document.objects.count(), 1)

    def _request_upload_interactive_view(self):
        logging.getLogger('django.request').setLevel(level=logging.CRITICAL)

        return self.get(
            viewname='sources:upload_interactive', data={
                'document_type_id': self.document_type.pk,
            }
        )

    def test_upload_interactive_view_no_permission(self):
        response = self._request_upload_interactive_view()
        self.assertEqual(response.status_code, 403)

    def test_upload_interactive_view_with_access(self):
        self.grant_access(
            permission=permission_document_create, obj=self.document_type
        )
        response = self._request_upload_interactive_view()
        self.assertContains(
            response=response, text=self.source.label, status_code=200
        )


class DocumentUploadIssueTestCase(GenericDocumentViewTestCase):
    auto_upload_document = False

    def test_issue_25(self):
        self.login_admin_user()

        # Create new webform source
        self.post(
            viewname='sources:setup_source_create',
            args=(SOURCE_CHOICE_WEB_FORM,),
            data={'label': 'test', 'uncompress': 'n', 'enabled': True}
        )
        self.assertEqual(WebFormSource.objects.count(), 1)

        # Upload the test document
        with open(TEST_SMALL_DOCUMENT_PATH, mode='rb') as file_descriptor:
            self.post(
                viewname='sources:upload_interactive', data={
                    'document-language': 'eng',
                    'source-file': file_descriptor,
                    'document_type_id': self.document_type.pk
                }
            )
        self.assertEqual(Document.objects.count(), 1)

        document = Document.objects.first()
        # Test for issue 25 during creation
        # ** description fields was removed from upload from **
        self.assertEqual(document.description, '')

        # Reset description
        document.description = TEST_DOCUMENT_DESCRIPTION
        document.save()
        self.assertEqual(document.description, TEST_DOCUMENT_DESCRIPTION)

        # Test for issue 25 during editing
        self.post(
            viewname='documents:document_edit', args=(document.pk,), data={
                'description': TEST_DOCUMENT_DESCRIPTION,
                'language': document.language, 'label': document.label
            }
        )
        # Fetch document again and test description
        document = Document.objects.first()
        self.assertEqual(document.description, TEST_DOCUMENT_DESCRIPTION)


class NewDocumentVersionViewTestCase(GenericDocumentViewTestCase):
    def test_new_version_block(self):
        """
        Gitlab issue #231
        User shown option to upload new version of a document even though it
        is blocked by checkout - v2.0.0b2

        Expected results:
            - Link to upload version view should not resolve
            - Upload version view should reject request
        """
        self.login_admin_user()

        NewVersionBlock.objects.block(self.document)

        response = self.post(
            viewname='sources:upload_version', args=(self.document.pk,),
            follow=True
        )

        self.assertContains(
            response, text='blocked from uploading',
            status_code=200
        )

        response = self.get(
            'documents:document_version_list', args=(self.document.pk,),
            follow=True
        )

        # Needed by the url view resolver
        response.context.current_app = None
        resolved_link = link_upload_version.resolve(context=response.context)

        self.assertEqual(resolved_link, None)


class StagingFolderViewTestCase(GenericViewTestCase):
    def setUp(self):
        super(StagingFolderViewTestCase, self).setUp()
        self.temporary_directory = mkdtemp()
        shutil.copy(TEST_SMALL_DOCUMENT_PATH, self.temporary_directory)
        self.filename = os.path.basename(TEST_SMALL_DOCUMENT_PATH)
        self.login_user()

    def tearDown(self):
        fs_cleanup(self.temporary_directory)
        super(StagingFolderViewTestCase, self).tearDown()

    def _request_staging_file_delete_view(self, staging_file):
        return self.post(
            viewname='sources:staging_file_delete', args=(
                self.staging_folder.pk, staging_file.encoded_filename
            )
        )

    def _create_staging_folder(self):
        self.staging_folder = StagingFolderSource.objects.create(
            label=TEST_SOURCE_LABEL,
            folder_path=self.temporary_directory,
            preview_width=TEST_STAGING_PREVIEW_WIDTH,
            uncompress=TEST_SOURCE_UNCOMPRESS_N,
        )

    def test_staging_folder_delete_no_permission(self):
        self._create_staging_folder()

        self.assertEqual(len(list(self.staging_folder.get_files())), 1)

        staging_file = list(self.staging_folder.get_files())[0]

        response = self._request_staging_file_delete_view(
            staging_file=staging_file
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(list(self.staging_folder.get_files())), 1)

    def test_staging_folder_delete_with_permission(self):
        self._create_staging_folder()
        self.grant_permission(permission=permission_staging_file_delete)

        self.assertEqual(len(list(self.staging_folder.get_files())), 1)

        staging_file = list(self.staging_folder.get_files())[0]

        response = self._request_staging_file_delete_view(
            staging_file=staging_file
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(list(self.staging_folder.get_files())), 0)


class SourcesViewsTestCase(GenericViewTestCase):
    def setUp(self):
        super(SourcesViewsTestCase, self).setUp()
        self.login_user()

    def _create_web_source(self):
        self.source = WebFormSource.objects.create(
            enabled=True, label=TEST_SOURCE_LABEL,
            uncompress=TEST_SOURCE_UNCOMPRESS_N
        )

    def _request_setup_source_list_view(self):
        return self.get(viewname='sources:setup_source_list')

    def test_source_list_view_no_permission(self):
        self._create_web_source()

        response = self._request_setup_source_list_view()
        self.assertEqual(response.status_code, 403)

    def test_source_list_view_with_permission(self):
        self._create_web_source()

        self.grant_permission(permission=permission_sources_setup_view)

        response = self._request_setup_source_list_view()
        self.assertContains(
            response=response, text=self.source.label, status_code=200
        )

    def _request_setup_source_create_view(self):
        return self.post(
            args=(SOURCE_CHOICE_WEB_FORM,),
            viewname='sources:setup_source_create', data={
                'enabled': True, 'label': TEST_SOURCE_LABEL,
                'uncompress': TEST_SOURCE_UNCOMPRESS_N
            }
        )

    def test_source_create_view_no_permission(self):
        self.grant_permission(permission=permission_sources_setup_view)

        response = self._request_setup_source_create_view()
        self.assertEqual(response.status_code, 403)

        self.assertEqual(WebFormSource.objects.count(), 0)

    def test_source_create_view_with_permission(self):
        self.grant_permission(permission=permission_sources_setup_create)
        self.grant_permission(permission=permission_sources_setup_view)

        response = self._request_setup_source_create_view()
        self.assertEquals(response.status_code, 302)

        webform_source = WebFormSource.objects.first()
        self.assertEqual(webform_source.label, TEST_SOURCE_LABEL)
        self.assertEqual(webform_source.uncompress, TEST_SOURCE_UNCOMPRESS_N)

    def _request_setup_source_delete_view(self):
        return self.post(
            args=(self.source.pk,),
            viewname='sources:setup_source_delete'
        )

    def test_source_delete_view_with_permission(self):
        self._create_web_source()

        self.grant_permission(permission=permission_sources_setup_delete)
        self.grant_permission(permission=permission_sources_setup_view)

        response = self._request_setup_source_delete_view()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(WebFormSource.objects.count(), 0)

    def test_source_delete_view_no_permission(self):
        self._create_web_source()

        self.grant_permission(permission=permission_sources_setup_view)

        response = self._request_setup_source_delete_view()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(WebFormSource.objects.count(), 1)
