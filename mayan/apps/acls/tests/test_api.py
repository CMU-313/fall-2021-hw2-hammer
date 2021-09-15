from __future__ import absolute_import, unicode_literals

from django.contrib.contenttypes.models import ContentType

from rest_framework import status

from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.tests import DocumentTestMixin
from mayan.apps.permissions.tests.literals import TEST_ROLE_LABEL
from mayan.apps.rest_api.tests import BaseAPITestCase

from ..models import AccessControlList
from ..permissions import permission_acl_view


class ACLAPITestCase(DocumentTestMixin, BaseAPITestCase):
    def setUp(self):
        super(ACLAPITestCase, self).setUp()
        self.login_admin_user()

        self.document_content_type = ContentType.objects.get_for_model(
            self.document
        )

    def _create_acl(self):
        self.acl = AccessControlList.objects.create(
            content_object=self.document,
            role=self.role
        )

        self.acl.permissions.add(permission_document_view.stored_permission)

    def test_object_acl_list_view(self):
        self._create_acl()

        response = self.get(
            viewname='rest_api:accesscontrollist-list',
            args=(
                self.document_content_type.app_label,
                self.document_content_type.model,
                self.document.pk
            )
        )

        self.assertEqual(
            response.data['results'][0]['content_type']['app_label'],
            self.document_content_type.app_label
        )
        self.assertEqual(
            response.data['results'][0]['role']['label'], TEST_ROLE_LABEL
        )

    def test_object_acl_delete_view(self):
        self._create_acl()

        response = self.delete(
            viewname='rest_api:accesscontrollist-detail',
            args=(
                self.document_content_type.app_label,
                self.document_content_type.model,
                self.document.pk, self.acl.pk
            )
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(AccessControlList.objects.count(), 0)

    def test_object_acl_detail_view(self):
        self._create_acl()

        response = self.get(
            viewname='rest_api:accesscontrollist-detail',
            args=(
                self.document_content_type.app_label,
                self.document_content_type.model,
                self.document.pk, self.acl.pk
            )
        )
        self.assertEqual(
            response.data['content_type']['app_label'],
            self.document_content_type.app_label
        )
        self.assertEqual(
            response.data['role']['label'], TEST_ROLE_LABEL
        )

    def test_object_acl_permission_delete_view(self):
        self._create_acl()
        permission = self.acl.permissions.first()

        response = self.delete(
            viewname='rest_api:accesscontrollist-permission-detail',
            args=(
                self.document_content_type.app_label,
                self.document_content_type.model,
                self.document.pk, self.acl.pk,
                permission.pk
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.acl.permissions.count(), 0)

    def test_object_acl_permission_detail_view(self):
        self._create_acl()
        permission = self.acl.permissions.first()

        response = self.get(
            viewname='rest_api:accesscontrollist-permission-detail',
            args=(
                self.document_content_type.app_label,
                self.document_content_type.model,
                self.document.pk, self.acl.pk,
                permission.pk
            )
        )

        self.assertEqual(
            response.data['pk'], permission_document_view.pk
        )

    def test_object_acl_permission_list_view(self):
        self._create_acl()

        response = self.get(
            viewname='rest_api:accesscontrollist-permission-list',
            args=(
                self.document_content_type.app_label,
                self.document_content_type.model,
                self.document.pk, self.acl.pk
            )
        )

        self.assertEqual(
            response.data['results'][0]['pk'],
            permission_document_view.pk
        )

    def test_object_acl_permission_list_post_view(self):
        self._create_acl()

        response = self.post(
            viewname='rest_api:accesscontrollist-permission-list',
            args=(
                self.document_content_type.app_label,
                self.document_content_type.model,
                self.document.pk, self.acl.pk
            ), data={'permission_pk': permission_acl_view.pk}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertQuerysetEqual(
            ordered=False, qs=self.acl.permissions.all(), values=(
                repr(permission_document_view.stored_permission),
                repr(permission_acl_view.stored_permission)
            )
        )

    def test_object_acl_post_no_permissions_added_view(self):
        response = self.post(
            viewname='rest_api:accesscontrollist-list',
            args=(
                self.document_content_type.app_label,
                self.document_content_type.model,
                self.document.pk
            ), data={'role_pk': self.role.pk}
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            self.document.acls.first().role, self.role
        )
        self.assertEqual(
            self.document.acls.first().content_object, self.document
        )
        self.assertEqual(
            self.document.acls.first().permissions.count(), 0
        )

    def test_object_acl_post_with_permissions_added_view(self):
        response = self.post(
            viewname='rest_api:accesscontrollist-list',
            args=(
                self.document_content_type.app_label,
                self.document_content_type.model,
                self.document.pk
            ), data={
                'role_pk': self.role.pk,
                'permissions_pk_list': permission_acl_view.pk

            }
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            self.document.acls.first().content_object, self.document
        )
        self.assertEqual(
            self.document.acls.first().role, self.role
        )
        self.assertEqual(
            self.document.acls.first().permissions.first(),
            permission_acl_view.stored_permission
        )
