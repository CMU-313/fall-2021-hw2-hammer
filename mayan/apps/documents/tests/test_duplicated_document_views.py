from ..permissions import permission_document_view

from .base import GenericDocumentViewTestCase
from .mixins import DuplicatedDocumentsViewsTestMixin


class DuplicatedDocumentsViewsTestCase(
    DuplicatedDocumentsViewsTestMixin, GenericDocumentViewTestCase
):
    def test_document_duplicates_list_no_permission(self):
        self._upload_duplicate_document()

        response = self._request_document_duplicates_list_view()
        self.assertEqual(response.status_code, 404)

    def test_document_duplicates_list_with_access(self):
        self._upload_duplicate_document()
        self.grant_access(
            obj=self.test_documents[0],
            permission=permission_document_view
        )
        self.grant_access(
            obj=self.test_documents[1],
            permission=permission_document_view
        )

        response = self._request_document_duplicates_list_view()
        self.assertContains(
            response=response, status_code=200,
            text=self.test_documents[0].label
        )

    def test_document_trashed_duplicates_list_with_full_access(self):
        self._upload_duplicate_document()
        self.grant_access(
            obj=self.test_documents[0],
            permission=permission_document_view
        )
        self.grant_access(
            obj=self.test_documents[1],
            permission=permission_document_view
        )
        self.test_documents[1].delete()

        response = self._request_document_duplicates_list_view()
        self.assertContains(
            response=response, status_code=200,
            text=self.test_documents[0].pk
        )
        self.assertNotContains(
            response=response, status_code=200,
            text=self.test_documents[1].pk
        )

    def test_duplicated_document_list_no_permission(self):
        self._upload_duplicate_document()

        response = self._request_duplicated_document_list_view()
        self.assertNotContains(
            response=response, status_code=200,
            text=self.test_documents[0].label
        )

    def test_duplicated_document_list_with_access(self):
        self._upload_duplicate_document()
        self.grant_access(
            obj=self.test_documents[0],
            permission=permission_document_view
        )
        self.grant_access(
            obj=self.test_documents[1],
            permission=permission_document_view
        )

        response = self._request_duplicated_document_list_view()
        self.assertContains(
            response=response, status_code=200,
            text=self.test_documents[0].label
        )

    def test_duplicated_trashed_document_list_with_access(self):
        self._upload_duplicate_document()
        self.grant_access(
            obj=self.test_documents[0],
            permission=permission_document_view
        )
        self.grant_access(
            obj=self.test_documents[1],
            permission=permission_document_view
        )
        self.test_documents[1].delete()

        response = self._request_duplicated_document_list_view()
        self.assertNotContains(
            response=response, status_code=200,
            text=self.test_documents[0].pk
        )
        self.assertNotContains(
            response=response, status_code=200,
            text=self.test_documents[1].pk
        )
