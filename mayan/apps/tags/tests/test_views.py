from __future__ import unicode_literals

from mayan.apps.common.tests import GenericViewTestCase
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.tests import GenericDocumentViewTestCase

from ..models import Tag
from ..permissions import (
    permission_tag_attach, permission_tag_create, permission_tag_delete,
    permission_tag_edit, permission_tag_remove, permission_tag_view
)

from .literals import (
    TEST_TAG_COLOR, TEST_TAG_COLOR_EDITED, TEST_TAG_LABEL,
    TEST_TAG_LABEL_EDITED
)
from .mixins import TagTestMixin


class TagViewTestCase(TagTestMixin, GenericViewTestCase):
    def test_tag_create_view_no_permissions(self):
        self.login_user()

        response = self._request_tag_create_view()
        self.assertEqual(response.status_code, 403)

        self.assertEqual(Tag.objects.count(), 0)

    def test_tag_create_view_with_permissions(self):
        self.login_user()

        self.grant_permission(permission=permission_tag_create)
        response = self._request_tag_create_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Tag.objects.count(), 1)
        tag = Tag.objects.first()
        self.assertEqual(tag.label, TEST_TAG_LABEL)
        self.assertEqual(tag.color, TEST_TAG_COLOR)

    def test_tag_delete_view_no_permissions(self):
        self.login_user()
        self._create_tag()

        response = self._request_tag_delete_view()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Tag.objects.count(), 1)

    def test_tag_delete_view_with_access(self):
        self.login_user()
        self._create_tag()

        self.grant_access(obj=self.tag, permission=permission_tag_delete)

        response = self._request_tag_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Tag.objects.count(), 0)

    def test_tag_multiple_delete_view_no_permissions(self):
        self.login_user()
        self._create_tag()

        response = self._request_multiple_delete_view()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Tag.objects.count(), 1)

    def test_tag_multiple_delete_view_with_access(self):
        self.login_user()
        self._create_tag()

        self.grant_access(obj=self.tag, permission=permission_tag_delete)

        response = self._request_multiple_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Tag.objects.count(), 0)

    def test_tag_edit_view_no_permissions(self):
        self.login_user()
        self._create_tag()

        response = self._request_edit_tag_view()
        self.assertEqual(response.status_code, 403)
        tag = Tag.objects.get(pk=self.tag.pk)
        self.assertEqual(tag.label, TEST_TAG_LABEL)
        self.assertEqual(tag.color, TEST_TAG_COLOR)

    def test_tag_edit_view_with_access(self):
        self.login_user()
        self._create_tag()

        self.grant_access(obj=self.tag, permission=permission_tag_edit)

        response = self._request_edit_tag_view()
        self.assertEqual(response.status_code, 302)
        tag = Tag.objects.get(pk=self.tag.pk)
        self.assertEqual(tag.label, TEST_TAG_LABEL_EDITED)
        self.assertEqual(tag.color, TEST_TAG_COLOR_EDITED)


class TagDocumentsViewTestCase(TagTestMixin, GenericDocumentViewTestCase):
    def _request_document_list_view(self):
        return self.get(viewname='documents:document_list')

    def test_document_tags_widget_no_permissions(self):
        self.login_user()
        self._create_tag()

        self.tag.documents.add(self.document)
        response = self._request_document_list_view()
        self.assertNotContains(
            response=response, text=TEST_TAG_LABEL, status_code=200
        )

    def test_document_tags_widget_with_access(self):
        self.login_user()
        self._create_tag()

        self.tag.documents.add(self.document)

        self.grant_access(obj=self.tag, permission=permission_tag_view)
        self.grant_access(
            obj=self.document, permission=permission_document_view
        )

        response = self._request_document_list_view()
        self.assertContains(
            response=response, text=TEST_TAG_LABEL, status_code=200
        )

    def test_document_attach_tag_view_no_permission(self):
        self.login_user()
        self._create_tag()

        self.assertEqual(self.document.tags.count(), 0)

        self.grant_access(obj=self.tag, permission=permission_tag_attach)

        response = self._request_attach_tag_view()
        # Redirect to previous URL and show warning message about having to
        # select at least one object.
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.document.tags.count(), 0)

    def test_document_attach_tag_view_with_access(self):
        self.login_user()
        self._create_tag()

        self.assertEqual(self.document.tags.count(), 0)

        self.grant_access(obj=self.document, permission=permission_tag_attach)
        self.grant_access(obj=self.tag, permission=permission_tag_attach)
        # permission_tag_view is needed because the form filters the
        # choices
        self.grant_access(obj=self.tag, permission=permission_tag_view)

        response = self._request_attach_tag_view()
        self.assertEqual(response.status_code, 302)

        self.assertQuerysetEqual(
            self.document.tags.all(), (repr(self.tag),)
        )

    def test_document_multiple_attach_tag_view_no_permission(self):
        self.login_user()
        self._create_tag()

        self.grant_permission(permission=permission_tag_view)

        response = self._request_multiple_attach_tag_view()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.document.tags.count(), 0)

    def test_document_multiple_attach_tag_view_with_access(self):
        self.login_user()
        self._create_tag()

        self.grant_access(obj=self.document, permission=permission_tag_attach)
        self.grant_access(obj=self.tag, permission=permission_tag_attach)

        # permission_tag_view is needed because the form filters the
        # choices
        self.grant_access(obj=self.tag, permission=permission_tag_view)

        response = self._request_multiple_attach_tag_view()
        self.assertEqual(response.status_code, 302)

        self.assertQuerysetEqual(
            self.document.tags.all(), (repr(self.tag),)
        )

    def test_single_document_multiple_tag_remove_view_no_permissions(self):
        self.login_user()
        self._create_tag()

        self.document.tags.add(self.tag)

        self.grant_access(obj=self.tag, permission=permission_tag_view)

        response = self._request_single_document_multiple_tag_remove_view()
        self.assertEqual(response.status_code, 200)

        self.assertQuerysetEqual(self.document.tags.all(), (repr(self.tag),))

    def test_single_document_multiple_tag_remove_view_with_access(self):
        self.login_user()
        self._create_tag()

        self.document.tags.add(self.tag)

        self.grant_access(obj=self.document, permission=permission_tag_remove)
        self.grant_access(obj=self.tag, permission=permission_tag_remove)
        self.grant_access(obj=self.tag, permission=permission_tag_view)

        response = self._request_single_document_multiple_tag_remove_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(self.document.tags.count(), 0)

    def test_multiple_documents_selection_tag_remove_view_no_permissions(self):
        self.login_user()
        self._create_tag()

        self.document.tags.add(self.tag)

        self.grant_access(obj=self.tag, permission=permission_tag_view)

        response = self._request_multiple_documents_selection_tag_remove_view()
        self.assertEqual(response.status_code, 200)

        self.assertQuerysetEqual(self.document.tags.all(), (repr(self.tag),))

    def test_multiple_documents_selection_tag_remove_view_with_access(self):
        self.login_user()
        self._create_tag()

        self.document.tags.add(self.tag)

        self.grant_access(obj=self.document, permission=permission_tag_remove)
        self.grant_access(obj=self.tag, permission=permission_tag_remove)
        self.grant_access(obj=self.tag, permission=permission_tag_view)

        response = self._request_multiple_documents_selection_tag_remove_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(self.document.tags.count(), 0)
