from __future__ import unicode_literals

from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.tests.base import GenericDocumentViewTestCase
from mayan.apps.sources.links import link_document_version_upload

from ..literals import STATE_CHECKED_OUT, STATE_LABELS
from ..models import DocumentCheckout
from ..permissions import (
    permission_document_check_in, permission_document_check_in_override,
    permission_document_check_out, permission_document_check_out_detail_view
)

from .mixins import DocumentCheckoutTestMixin, DocumentCheckoutViewTestMixin


class DocumentCheckoutViewTestCase(
    DocumentCheckoutTestMixin, DocumentCheckoutViewTestMixin,
    GenericDocumentViewTestCase
):
    def test_document_check_in_get_view_no_permission(self):
        self._check_out_test_document()

        response = self._request_test_document_check_in_get_view()
        self.assertNotContains(
            response=response, text=self.test_document.label, status_code=404
        )

        self.assertTrue(self.test_document.is_checked_out())

    def test_document_check_in_get_view_with_access(self):
        self._check_out_test_document()

        self.grant_access(
            obj=self.test_document, permission=permission_document_check_in
        )

        response = self._request_test_document_check_in_get_view()
        self.assertContains(
            response=response, text=self.test_document.label, status_code=200
        )

        self.assertTrue(self.test_document.is_checked_out())

    def test_document_check_in_post_view_no_permission(self):
        self._check_out_test_document()

        response = self._request_test_document_check_in_post_view()
        self.assertEqual(response.status_code, 404)

        self.assertTrue(self.test_document.is_checked_out())

    def test_document_check_in_post_view_with_access(self):
        self._check_out_test_document()

        self.grant_access(
            obj=self.test_document, permission=permission_document_check_in
        )

        response = self._request_test_document_check_in_post_view()
        self.assertEqual(response.status_code, 302)

        self.assertFalse(self.test_document.is_checked_out())
        self.assertFalse(
            DocumentCheckout.objects.is_checked_out(
                document=self.test_document
            )
        )

    def test_document_multiple_check_in_post_view_no_permission(self):
        # Upload second document
        self.upload_document()

        self._check_out_test_document(document=self.test_documents[0])
        self._check_out_test_document(document=self.test_documents[1])

        response = self._request_test_document_multiple_check_in_post_view()
        self.assertEqual(response.status_code, 404)

        self.assertTrue(self.test_documents[0].is_checked_out())
        self.assertTrue(self.test_documents[1].is_checked_out())
        self.assertTrue(
            DocumentCheckout.objects.is_checked_out(
                document=self.test_documents[0]
            )
        )
        self.assertTrue(
            DocumentCheckout.objects.is_checked_out(
                document=self.test_documents[1]
            )
        )

    def test_document_multiple_check_in_post_view_with_document_0_access(self):
        # Upload second document
        self.upload_document()

        self._check_out_test_document(document=self.test_documents[0])
        self._check_out_test_document(document=self.test_documents[1])

        self.grant_access(
            obj=self.test_documents[0], permission=permission_document_check_in
        )

        response = self._request_test_document_multiple_check_in_post_view()
        self.assertEqual(response.status_code, 302)

        self.assertFalse(self.test_documents[0].is_checked_out())
        self.assertTrue(self.test_documents[1].is_checked_out())
        self.assertFalse(
            DocumentCheckout.objects.is_checked_out(
                document=self.test_documents[0]
            )
        )
        self.assertTrue(
            DocumentCheckout.objects.is_checked_out(
                document=self.test_documents[1]
            )
        )

    def test_document_multiple_check_in_post_view_with_access(self):
        # Upload second document
        self.upload_document()

        self._check_out_test_document(document=self.test_documents[0])
        self._check_out_test_document(document=self.test_documents[1])

        self.grant_access(
            obj=self.test_documents[0], permission=permission_document_check_in
        )
        self.grant_access(
            obj=self.test_documents[1], permission=permission_document_check_in
        )

        response = self._request_test_document_multiple_check_in_post_view()
        self.assertEqual(response.status_code, 302)

        self.assertFalse(self.test_documents[0].is_checked_out())
        self.assertFalse(self.test_documents[1].is_checked_out())
        self.assertFalse(
            DocumentCheckout.objects.is_checked_out(
                document=self.test_documents[0]
            )
        )
        self.assertFalse(
            DocumentCheckout.objects.is_checked_out(
                document=self.test_documents[1]
            )
        )

    def test_document_check_out_view_no_permission(self):
        response = self._request_test_document_check_out_view()
        self.assertEqual(response.status_code, 404)

        self.assertFalse(self.test_document.is_checked_out())

    def test_document_check_out_view_with_access(self):
        self.grant_access(
            obj=self.test_document, permission=permission_document_check_out
        )
        self.grant_access(
            obj=self.test_document,
            permission=permission_document_check_out_detail_view
        )

        response = self._request_test_document_check_out_view()
        self.assertEqual(response.status_code, 302)

        self.assertTrue(self.test_document.is_checked_out())

    def test_document_multiple_check_out_post_view_no_permission(self):
        # Upload second document
        self.upload_document()

        self.grant_access(
            obj=self.test_documents[0],
            permission=permission_document_check_out_detail_view
        )
        self.grant_access(
            obj=self.test_documents[1],
            permission=permission_document_check_out_detail_view
        )

        response = self._request_test_document_multiple_check_out_post_view()
        self.assertEqual(response.status_code, 404)

        self.assertFalse(self.test_documents[0].is_checked_out())
        self.assertFalse(self.test_documents[1].is_checked_out())
        self.assertFalse(
            DocumentCheckout.objects.is_checked_out(
                document=self.test_documents[0]
            )
        )
        self.assertFalse(
            DocumentCheckout.objects.is_checked_out(
                document=self.test_documents[1]
            )
        )

    def test_document_multiple_check_out_post_view_with_document_access(self):
        # Upload second document
        self.upload_document()

        self.grant_access(
            obj=self.test_documents[0], permission=permission_document_check_out
        )
        self.grant_access(
            obj=self.test_documents[0],
            permission=permission_document_check_out_detail_view
        )
        self.grant_access(
            obj=self.test_documents[1],
            permission=permission_document_check_out_detail_view
        )

        response = self._request_test_document_multiple_check_out_post_view()
        self.assertEqual(response.status_code, 302)

        self.assertTrue(self.test_documents[0].is_checked_out())
        self.assertFalse(self.test_documents[1].is_checked_out())
        self.assertTrue(
            DocumentCheckout.objects.is_checked_out(
                document=self.test_documents[0]
            )
        )
        self.assertFalse(
            DocumentCheckout.objects.is_checked_out(
                document=self.test_documents[1]
            )
        )

    def test_document_multiple_check_out_post_view_with_access(self):
        # Upload second document
        self.upload_document()

        self.grant_access(
            obj=self.test_documents[0], permission=permission_document_check_out
        )
        self.grant_access(
            obj=self.test_documents[1], permission=permission_document_check_out
        )
        self.grant_access(
            obj=self.test_documents[0],
            permission=permission_document_check_out_detail_view
        )
        self.grant_access(
            obj=self.test_documents[1],
            permission=permission_document_check_out_detail_view
        )

        response = self._request_test_document_multiple_check_out_post_view()
        self.assertEqual(response.status_code, 302)

        self.assertTrue(self.test_documents[0].is_checked_out())
        self.assertTrue(self.test_documents[1].is_checked_out())
        self.assertTrue(
            DocumentCheckout.objects.is_checked_out(
                document=self.test_documents[0]
            )
        )
        self.assertTrue(
            DocumentCheckout.objects.is_checked_out(
                document=self.test_documents[1]
            )
        )

    def test_document_check_out_detail_view_no_permission(self):
        self._check_out_test_document()

        response = self._request_test_document_check_out_detail_view()

        self.assertNotContains(
            response, text=STATE_LABELS[STATE_CHECKED_OUT], status_code=404
        )

    def test_document_check_out_detail_view_with_access(self):
        self._check_out_test_document()

        self.grant_access(
            obj=self.test_document,
            permission=permission_document_check_out_detail_view
        )

        response = self._request_test_document_check_out_detail_view()
        self.assertContains(
            response, text=STATE_LABELS[STATE_CHECKED_OUT], status_code=200
        )

    def test_document_check_out_list_view_no_permission(self):
        self._check_out_test_document()

        self.grant_access(
            obj=self.test_document,
            permission=permission_document_view
        )

        response = self._request_test_document_check_out_list_view()
        self.assertNotContains(
            response=response, text=self.test_document.label, status_code=200
        )

    def test_document_check_out_list_view_with_access(self):
        self._check_out_test_document()

        self.grant_access(
            obj=self.test_document,
            permission=permission_document_check_out_detail_view
        )
        self.grant_access(
            obj=self.test_document,
            permission=permission_document_view
        )

        response = self._request_test_document_check_out_list_view()
        self.assertContains(
            response=response, text=self.test_document.label, status_code=200
        )

    def test_document_check_in_forcefull_view_no_permission(self):
        # Gitlab issue #237
        # Forcefully checking in a document by a user without adequate
        # permissions throws out an error
        self._create_test_user()
        # Check out document as test_user
        self._check_out_test_document(user=self.test_user)

        self.grant_access(
            obj=self.test_document, permission=permission_document_check_in
        )

        response = self.post(
            viewname='checkouts:check_in_document', kwargs={
                'pk': self.test_document.pk
            }
        )
        self.assertEqual(response.status_code, 302)

        self.assertTrue(self.test_document.is_checked_out())

    def test_document_check_in_forcefull_view_with_access(self):
        self._create_test_user()
        # Check out document as test_user
        self._check_out_test_document(user=self.test_user)

        self.grant_access(
            obj=self.test_document,
            permission=permission_document_check_in_override
        )

        # Check in document as test_case_user
        response = self.post(
            viewname='checkouts:check_in_document', kwargs={
                'pk': self.test_document.pk
            }
        )
        self.assertEqual(response.status_code, 302)

        self.assertFalse(self.test_document.is_checked_out())


class NewVersionBlockViewTestCase(
    DocumentCheckoutTestMixin, DocumentCheckoutViewTestMixin,
    GenericDocumentViewTestCase
):
    def test_document_check_out_block_new_version(self):
        """
        Gitlab issue #231
        User shown option to upload new version of a document even though it
        is blocked by checkout - v2.0.0b2

        Expected results:
            - Link to upload version view should not resolve
            - Upload version view should reject request
        """
        self._create_test_case_superuser()
        self._check_out_test_document()
        self.login_superuser()

        response = self.post(
            viewname='sources:document_version_upload', kwargs={
                'document_pk': self.test_document.pk
            }, follow=True
        )

        self.assertContains(
            response=response, text='blocked from uploading',
            status_code=200
        )

        response = self.get(
            viewname='documents:document_version_list', kwargs={
                'pk': self.test_document.pk
            }, follow=True
        )

        # Needed by the url view resolver
        response.context.current_app = None
        resolved_link = link_document_version_upload.resolve(
            context=response.context
        )

        self.assertEqual(resolved_link, None)
