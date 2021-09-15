from __future__ import unicode_literals

from ..models import FavoriteDocument
from ..permissions import permission_document_view

from .base import GenericDocumentViewTestCase


class FavoriteDocumentsTestCase(GenericDocumentViewTestCase):
    def _request_document_add_to_favorites_view(self):
        return self.post(
            viewname='documents:document_add_to_favorites',
            kwargs={'pk': self.test_document.pk}
        )

    def test_document_add_to_favorites_view_no_permission(self):
        response = self._request_document_add_to_favorites_view()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(FavoriteDocument.objects.count(), 0)

    def test_document_add_to_favorites_view_with_access(self):
        self.grant_access(
            obj=self.test_document, permission=permission_document_view
        )
        response = self._request_document_add_to_favorites_view()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FavoriteDocument.objects.count(), 1)

    def _document_add_to_favorites(self):
        FavoriteDocument.objects.add_for_user(
            document=self.test_document, user=self._test_case_user
        )

    def _request_document_list_favorites(self):
        return self.get(
            viewname='documents:document_list_favorites',
        )

    def test_document_list_favorites_view_no_permission(self):
        self._document_add_to_favorites()
        response = self._request_document_list_favorites()
        self.assertNotContains(
            response=response, text=self.test_document.label, status_code=200
        )

    def test_document_list_favorites_view_with_access(self):
        self._document_add_to_favorites()
        self.grant_access(
            obj=self.test_document, permission=permission_document_view
        )
        response = self._request_document_list_favorites()
        self.assertContains(
            response=response, text=self.test_document.label, status_code=200
        )

    def _request_document_remove_from_favorites(self):
        return self.post(
            viewname='documents:document_remove_from_favorites',
            kwargs={'pk': self.test_document.pk}
        )

    def test_document_remove_from_favorites_view_no_permission(self):
        self._document_add_to_favorites()
        response = self._request_document_remove_from_favorites()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(FavoriteDocument.objects.count(), 1)

    def test_document_remove_from_favorites_view_with_access(self):
        self._document_add_to_favorites()
        self.grant_access(
            obj=self.test_document, permission=permission_document_view
        )
        response = self._request_document_remove_from_favorites()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(FavoriteDocument.objects.count(), 0)
