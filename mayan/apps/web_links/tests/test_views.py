from __future__ import unicode_literals

from django.utils.encoding import force_text

from mayan.apps.common.tests import GenericViewTestCase
from mayan.apps.documents.tests import GenericDocumentViewTestCase

from ..models import WebLink
from ..permissions import (
    permission_web_link_create, permission_web_link_delete,
    permission_web_link_edit, permission_web_link_view,
    permission_web_link_instance_view
)

from .literals import TEST_WEB_LINK_TEMPLATE
from .mixins import WebLinkTestMixin, WebLinkViewTestMixin


class WebLinkViewTestCase(
    WebLinkTestMixin, WebLinkViewTestMixin, GenericViewTestCase
):
    def test_web_link_create_view_no_permissions(self):
        web_link_count = WebLink.objects.count()

        response = self._request_test_web_link_create_view()
        self.assertEqual(response.status_code, 403)

        self.assertEqual(WebLink.objects.count(), web_link_count)

    def test_web_link_create_view_with_permissions(self):
        self.grant_permission(permission=permission_web_link_create)

        web_link_count = WebLink.objects.count()

        response = self._request_test_web_link_create_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(WebLink.objects.count(), web_link_count + 1)

    def test_web_link_delete_view_no_permissions(self):
        self._create_test_web_link()

        web_link_count = WebLink.objects.count()

        response = self._request_test_web_link_delete_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(WebLink.objects.count(), web_link_count)

    def test_web_link_delete_view_with_access(self):
        self._create_test_web_link()

        self.grant_access(
            obj=self.test_web_link, permission=permission_web_link_delete
        )

        web_link_count = WebLink.objects.count()

        response = self._request_test_web_link_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(WebLink.objects.count(), web_link_count - 1)

    def test_web_link_edit_view_no_permissions(self):
        self._create_test_web_link()

        web_link_label = self.test_web_link.label

        response = self._request_test_web_link_edit_view()
        self.assertEqual(response.status_code, 404)

        self.test_web_link.refresh_from_db()
        self.assertEqual(self.test_web_link.label, web_link_label)

    def test_web_link_edit_view_with_access(self):
        self._create_test_web_link()

        self.grant_access(
            obj=self.test_web_link, permission=permission_web_link_edit
        )

        web_link_label = self.test_web_link.label

        response = self._request_test_web_link_edit_view()
        self.assertEqual(response.status_code, 302)

        self.test_web_link.refresh_from_db()
        self.assertNotEqual(self.test_web_link.label, web_link_label)

    def test_web_link_list_view_with_no_permission(self):
        self._create_test_web_link()

        response = self._request_test_web_link_list_view()
        self.assertNotContains(
            response=response, text=self.test_web_link.label, status_code=200
        )

    def test_web_link_list_view_with_access(self):
        self._create_test_web_link()

        self.grant_access(obj=self.test_web_link, permission=permission_web_link_view)

        response = self._request_test_web_link_list_view()
        self.assertContains(
            response=response, text=self.test_web_link.label, status_code=200
        )


class DocumentWebLinkViewTestCase(
    WebLinkTestMixin, WebLinkViewTestMixin, GenericDocumentViewTestCase
):
    def setUp(self):
        super(DocumentWebLinkViewTestCase, self).setUp()
        self._create_test_web_link()
        self.test_web_link.document_types.add(self.test_document_type)

    def test_document_web_links_list_view_no_permissions(self):
        response = self._request_test_document_web_link_list_view()
        self.assertNotContains(
            response=response, text=force_text(self.test_document),
            status_code=404
        )
        self.assertNotContains(
            response=response, text=force_text(self.test_web_link),
            status_code=404
        )

    def test_document_web_links_list_view_with_document_access(self):
        self.grant_access(
            obj=self.test_document,
            permission=permission_web_link_instance_view
        )

        response = self._request_test_document_web_link_list_view()
        self.assertContains(
            response=response, text=force_text(self.test_document),
            status_code=200
        )
        self.assertNotContains(
            response=response, text=force_text(self.test_web_link),
            status_code=200
        )

    def test_document_web_links_list_view_with_web_link_access(self):
        self.grant_access(
            obj=self.test_web_link,
            permission=permission_web_link_instance_view
        )

        response = self._request_test_document_web_link_list_view()
        self.assertNotContains(
            response=response, text=force_text(self.test_document),
            status_code=404
        )
        self.assertNotContains(
            response=response, text=force_text(self.test_web_link),
            status_code=404
        )

    def test_document_web_links_list_view_with_full_access(self):
        self.grant_access(
            obj=self.test_document,
            permission=permission_web_link_instance_view
        )
        self.grant_access(
            obj=self.test_web_link,
            permission=permission_web_link_instance_view
        )

        response = self._request_test_document_web_link_list_view()
        self.assertContains(
            response=response, text=force_text(self.test_document),
            status_code=200
        )
        self.assertContains(
            response=response, text=force_text(self.test_web_link),
            status_code=200
        )

    def test_document_resolved_web_link_view_no_permissions(self):
        response = self._request_test_document_web_link_instance_view()
        self.assertEqual(response.status_code, 404)

    def test_document_resolved_web_link_view_with_document_access(self):
        self.grant_access(
            obj=self.test_document,
            permission=permission_web_link_instance_view
        )

        response = self._request_test_document_web_link_instance_view()
        self.assertEqual(response.status_code, 404)

    def test_document_resolved_web_link_view_with_web_link_access(self):
        self.grant_access(
            obj=self.test_web_link,
            permission=permission_web_link_instance_view
        )

        response = self._request_test_document_web_link_instance_view()
        self.assertEqual(response.status_code, 404)

    def test_document_resolved_web_link_view_with_full_access(self):
        self.grant_access(
            obj=self.test_document,
            permission=permission_web_link_instance_view
        )
        self.grant_access(
            obj=self.test_web_link,
            permission=permission_web_link_instance_view
        )

        response = self._request_test_document_web_link_instance_view()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, TEST_WEB_LINK_TEMPLATE.replace(
                '{{ document.uuid }}', force_text(self.test_document.uuid)
            )
        )
