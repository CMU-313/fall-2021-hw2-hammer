from rest_framework import status

from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.documents.tests.base import DocumentTestMixin
from mayan.apps.rest_api.tests.base import BaseAPITestCase

from ..models import SmartLink, SmartLinkCondition
from ..permissions import (
    permission_smart_link_create, permission_smart_link_delete,
    permission_smart_link_edit, permission_smart_link_view
)

from .literals import (
    TEST_SMART_LINK_CONDITION_EXPRESSION,
    TEST_SMART_LINK_CONDITION_EXPRESSION_EDITED,
    TEST_SMART_LINK_CONDITION_OPERATOR, TEST_SMART_LINK_LABEL_EDITED,
    TEST_SMART_LINK_LABEL
)
from .mixins import (
    ResolvedSmartLinkAPIViewTestMixin, SmartLinkAPIViewTestMixin,
    SmartLinkConditionAPIViewTestMixin, SmartLinkTestMixin
)


class ResolvedSmartLinkAPIViewTestCase(
    DocumentTestMixin, SmartLinkTestMixin,
    ResolvedSmartLinkAPIViewTestMixin, BaseAPITestCase
):
    def setUp(self):
        super(ResolvedSmartLinkAPIViewTestCase, self).setUp()
        self._create_test_smart_link(add_test_document_type=True)
        self._create_test_smart_link_condition()

    def test_resolved_smart_link_detail_view_no_permission(self):
        response = self._request_resolved_smart_link_detail_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_resolved_smart_link_detail_view_with_document_access(self):
        self.grant_access(
            obj=self.test_document, permission=permission_document_view
        )

        response = self._request_resolved_smart_link_detail_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_resolved_smart_link_detail_view_with_smart_link_access(self):
        self.grant_access(
            obj=self.test_smart_link, permission=permission_smart_link_view
        )

        response = self._request_resolved_smart_link_detail_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_resolved_smart_link_detail_view_with_full_access(self):
        self.grant_access(
            obj=self.test_smart_link, permission=permission_smart_link_view
        )
        self.grant_access(
            obj=self.test_document, permission=permission_document_view
        )

        response = self._request_resolved_smart_link_detail_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.data['label'], TEST_SMART_LINK_LABEL
        )

    def test_resolved_smart_link_list_view_no_permission(self):
        response = self._request_resolved_smart_link_list_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertFalse('results' in response.data)

    def test_resolved_smart_link_list_view_with_document_access(self):
        self.grant_access(
            obj=self.test_document, permission=permission_document_view
        )

        response = self._request_resolved_smart_link_list_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['count'], 0)

    def test_resolved_smart_link_list_view_with_smart_link_access(self):
        self.grant_access(
            obj=self.test_smart_link, permission=permission_smart_link_view
        )
        response = self._request_resolved_smart_link_list_view()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse('results' in response.data)

    def test_resolved_smart_link_list_view_with_access(self):
        self.grant_access(
            obj=self.test_smart_link, permission=permission_smart_link_view
        )
        self.grant_access(
            obj=self.test_document, permission=permission_document_view
        )

        response = self._request_resolved_smart_link_list_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['label'], TEST_SMART_LINK_LABEL
        )

    def test_resolved_smart_link_document_list_view_no_permission(self):
        response = self._request_resolved_smart_link_document_list_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_resolved_smart_link_document_list_view_with_smart_link_access(self):
        self.grant_access(
            obj=self.test_smart_link, permission=permission_smart_link_view
        )

        response = self._request_resolved_smart_link_document_list_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_resolved_smart_link_document_list_view_with_document_access(self):
        self.grant_access(
            obj=self.test_document, permission=permission_document_view
        )
        response = self._request_resolved_smart_link_document_list_view()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_resolved_smart_link_document_list_view_with_full_access(self):
        self.grant_access(
            obj=self.test_document, permission=permission_document_view
        )
        self.grant_access(
            obj=self.test_smart_link, permission=permission_smart_link_view
        )

        response = self._request_resolved_smart_link_document_list_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['label'], self.test_document.label
        )


class SmartLinkAPIViewTestCase(
    DocumentTestMixin, SmartLinkTestMixin, SmartLinkAPIViewTestMixin,
    BaseAPITestCase
):
    auto_create_test_document_type = False
    auto_upload_test_document = False

    def test_smart_link_create_view_no_permission(self):
        response = self._request_test_smart_link_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(SmartLink.objects.count(), 0)

    def test_smart_link_create_view_with_permission(self):
        self.grant_permission(permission=permission_smart_link_create)

        response = self._request_test_smart_link_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        smart_link = SmartLink.objects.first()
        self.assertEqual(response.data['id'], smart_link.pk)
        self.assertEqual(response.data['label'], TEST_SMART_LINK_LABEL)

        self.assertEqual(SmartLink.objects.count(), 1)
        self.assertEqual(smart_link.label, TEST_SMART_LINK_LABEL)

    def test_smart_link_create_with_document_types_view_no_permission(self):
        self._create_test_document_type()

        response = self._request_test_smart_link_create_with_document_type_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(SmartLink.objects.count(), 0)

    def test_smart_link_create_with_document_types_view_with_permission(self):
        self._create_test_document_type()
        self.grant_permission(permission=permission_smart_link_create)

        response = self._request_test_smart_link_create_with_document_type_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        smart_link = SmartLink.objects.first()
        self.assertEqual(response.data['id'], smart_link.pk)
        self.assertEqual(response.data['label'], TEST_SMART_LINK_LABEL)

        self.assertEqual(SmartLink.objects.count(), 1)
        self.assertEqual(smart_link.label, TEST_SMART_LINK_LABEL)
        self.assertTrue(
            self.test_document_type in smart_link.document_types.all()
        )

    def test_smart_link_delete_view_no_permission(self):
        self._create_test_smart_link()

        response = self._request_test_smart_link_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(SmartLink.objects.count(), 1)

    def test_smart_link_delete_view_with_access(self):
        self._create_test_smart_link()
        self.grant_access(
            obj=self.test_smart_link, permission=permission_smart_link_delete
        )

        response = self._request_test_smart_link_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(SmartLink.objects.count(), 0)

    def test_smart_link_detail_view_no_permission(self):
        self._create_test_smart_link()

        response = self._request_test_smart_link_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertFalse('label' in response.data)

    def test_smart_link_detail_view_with_access(self):
        self._create_test_smart_link()
        self.grant_access(
            obj=self.test_smart_link, permission=permission_smart_link_view
        )

        response = self._request_test_smart_link_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            response.data['label'], TEST_SMART_LINK_LABEL
        )

    def test_smart_link_edit_view_via_patch_no_permission(self):
        self._create_test_document_type()
        self._create_test_smart_link()

        response = self._request_test_smart_link_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_smart_link.refresh_from_db()
        self.assertEqual(self.test_smart_link.label, TEST_SMART_LINK_LABEL)

    def test_smart_link_edit_view_via_patch_with_access(self):
        self._create_test_document_type()
        self._create_test_smart_link()
        self.grant_access(
            obj=self.test_smart_link, permission=permission_smart_link_edit
        )

        response = self._request_test_smart_link_edit_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_smart_link.refresh_from_db()
        self.assertEqual(
            self.test_smart_link.label, TEST_SMART_LINK_LABEL_EDITED
        )

    def test_smart_link_edit_view_via_put_no_permission(self):
        self._create_test_document_type()
        self._create_test_smart_link()

        response = self._request_test_smart_link_edit_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_smart_link.refresh_from_db()
        self.assertEqual(self.test_smart_link.label, TEST_SMART_LINK_LABEL)

    def test_smart_link_edit_view_via_put_with_access(self):
        self._create_test_document_type()
        self._create_test_smart_link()
        self.grant_access(
            obj=self.test_smart_link, permission=permission_smart_link_edit
        )

        response = self._request_test_smart_link_edit_put_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_smart_link.refresh_from_db()
        self.assertEqual(
            self.test_smart_link.label, TEST_SMART_LINK_LABEL_EDITED
        )


class SmartLinkConditionAPIViewTestCase(
    DocumentTestMixin, SmartLinkTestMixin,
    SmartLinkConditionAPIViewTestMixin, BaseAPITestCase
):
    auto_upload_test_document = False

    def setUp(self):
        super(SmartLinkConditionAPIViewTestCase, self).setUp()
        self._create_test_smart_link(add_test_document_type=True)

    def test_smart_link_condition_create_view_no_permission(self):
        response = self._request_smart_link_condition_create_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse('id' in response.data)

    def test_smart_link_condition_create_view_with_access(self):
        self.grant_access(
            obj=self.test_smart_link, permission=permission_smart_link_edit
        )

        response = self._request_smart_link_condition_create_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        smart_link_condition = SmartLinkCondition.objects.first()
        self.assertEqual(response.data['id'], smart_link_condition.pk)
        self.assertEqual(
            response.data['operator'], TEST_SMART_LINK_CONDITION_OPERATOR
        )

        self.assertEqual(SmartLinkCondition.objects.count(), 1)
        self.assertEqual(
            smart_link_condition.operator, TEST_SMART_LINK_CONDITION_OPERATOR
        )

    def test_smart_link_condition_delete_view_no_permission(self):
        self._create_test_smart_link_condition()

        response = self._request_smart_link_condition_delete_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(SmartLinkCondition.objects.count(), 1)

    def test_smart_link_condition_delete_view_with_access(self):
        self._create_test_smart_link_condition()

        self.grant_access(
            obj=self.test_smart_link, permission=permission_smart_link_edit
        )

        response = self._request_smart_link_condition_delete_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(SmartLinkCondition.objects.count(), 0)

    def test_smart_link_condition_detail_view_no_permission(self):
        self._create_test_smart_link_condition()

        response = self._request_smart_link_condition_detail_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertFalse('id' in response.data)

    def test_smart_link_condition_detail_view_with_access(self):
        self._create_test_smart_link_condition()

        self.grant_access(
            obj=self.test_smart_link, permission=permission_smart_link_view
        )

        response = self._request_smart_link_condition_detail_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['operator'], TEST_SMART_LINK_CONDITION_OPERATOR
        )

    def test_smart_link_condition_patch_view_no_permission(self):
        self._create_test_smart_link_condition()

        response = self._request_smart_link_condition_edit_view_via_patch()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.test_smart_link_condition.refresh_from_db()
        self.assertEqual(
            self.test_smart_link_condition.expression,
            TEST_SMART_LINK_CONDITION_EXPRESSION
        )

    def test_smart_link_condition_patch_view_with_access(self):
        self._create_test_smart_link_condition()

        self.grant_access(
            obj=self.test_smart_link, permission=permission_smart_link_edit
        )

        response = self._request_smart_link_condition_edit_view_via_patch()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_smart_link_condition.refresh_from_db()
        self.assertEqual(
            self.test_smart_link_condition.expression,
            TEST_SMART_LINK_CONDITION_EXPRESSION_EDITED
        )

    def test_smart_link_condition_put_view_no_permission(self):
        self._create_test_smart_link_condition()

        response = self._request_smart_link_condition_edit_view_via_put()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.test_smart_link_condition.refresh_from_db()
        self.assertEqual(
            self.test_smart_link_condition.expression,
            TEST_SMART_LINK_CONDITION_EXPRESSION
        )

    def test_smart_link_condition_put_view_with_access(self):
        self._create_test_smart_link_condition()

        self.grant_access(
            obj=self.test_smart_link, permission=permission_smart_link_edit
        )

        response = self._request_smart_link_condition_edit_view_via_put()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_smart_link_condition.refresh_from_db()
        self.assertEqual(
            self.test_smart_link_condition.expression,
            TEST_SMART_LINK_CONDITION_EXPRESSION_EDITED
        )
