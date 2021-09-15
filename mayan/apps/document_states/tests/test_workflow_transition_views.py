from mayan.apps.common.tests.base import GenericViewTestCase
from mayan.apps.documents.tests.base import GenericDocumentViewTestCase

from ..literals import WIDGET_CLASS_TEXTAREA
from ..models import WorkflowTransition
from ..permissions import (
    permission_workflow_edit, permission_workflow_transition,
    permission_workflow_view
)

from .literals import (
    TEST_WORKFLOW_TRANSITION_FIELD_HELP_TEXT,
    TEST_WORKFLOW_TRANSITION_FIELD_LABEL, TEST_WORKFLOW_TRANSITION_FIELD_NAME,
    TEST_WORKFLOW_TRANSITION_FIELD_TYPE, TEST_WORKFLOW_TRANSITION_LABEL,
    TEST_WORKFLOW_TRANSITION_LABEL_EDITED
)
from .mixins import (
    WorkflowTestMixin, WorkflowTransitionEventViewTestMixin,
    WorkflowTransitionFieldViewTestMixin, WorkflowViewTestMixin,
    WorkflowTransitionViewTestMixin
)


class WorkflowTransitionViewTestCase(
    WorkflowTestMixin, WorkflowViewTestMixin, WorkflowTransitionViewTestMixin,
    GenericViewTestCase
):
    def test_create_test_workflow_transition_no_access(self):
        self._create_test_workflow()
        self._create_test_workflow_states()

        response = self._request_test_workflow_transition_create_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(WorkflowTransition.objects.count(), 0)

    def test_create_test_workflow_transition_with_access(self):
        self._create_test_workflow()
        self._create_test_workflow_states()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_edit
        )

        response = self._request_test_workflow_transition_create_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(WorkflowTransition.objects.count(), 1)
        self.assertEqual(
            WorkflowTransition.objects.all()[0].label,
            TEST_WORKFLOW_TRANSITION_LABEL
        )
        self.assertEqual(
            WorkflowTransition.objects.all()[0].origin_state,
            self.test_workflow_state_1
        )
        self.assertEqual(
            WorkflowTransition.objects.all()[0].destination_state,
            self.test_workflow_state_2
        )

    def test_delete_workflow_transition_no_permissions(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        response = self._request_test_workflow_transition_delete_view()
        self.assertEqual(response.status_code, 404)

        self.assertTrue(
            self.test_workflow_transition in WorkflowTransition.objects.all()
        )

    def test_delete_workflow_transition_with_access(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        self.grant_access(permission=permission_workflow_edit, obj=self.test_workflow)

        response = self._request_test_workflow_transition_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            self.test_workflow_transition in WorkflowTransition.objects.all()
        )

    def test_edit_workflow_transition_no_access(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        response = self._request_test_workflow_transition_edit_view()
        self.assertEqual(response.status_code, 404)

        self.test_workflow_transition.refresh_from_db()
        self.assertEqual(
            self.test_workflow_transition.label, TEST_WORKFLOW_TRANSITION_LABEL
        )

    def test_edit_workflow_transition_with_access(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_edit
        )

        response = self._request_test_workflow_transition_edit_view()
        self.assertEqual(response.status_code, 302)

        self.test_workflow_transition.refresh_from_db()
        self.assertEqual(
            self.test_workflow_transition.label,
            TEST_WORKFLOW_TRANSITION_LABEL_EDITED
        )

    def test_workflow_transition_list_no_access(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        response = self._request_test_workflow_transition_list_view()
        self.assertNotContains(
            response=response, text=self.test_workflow_transition.label,
            status_code=404
        )

    def test_workflow_transition_list_with_access(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_view
        )

        response = self._request_test_workflow_transition_list_view()
        self.assertContains(
            response=response, text=self.test_workflow_transition.label,
            status_code=200
        )


class WorkflowTransitionEventViewTestCase(
    WorkflowTestMixin, WorkflowTransitionEventViewTestMixin,
    GenericDocumentViewTestCase
):

    def test_workflow_transition_event_list_no_access(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        response = self._request_test_workflow_transition_event_list_view()
        self.assertEqual(response.status_code, 404)

    def test_workflow_transition_event_list_with_access(self):
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_edit
        )

        response = self._request_test_workflow_transition_event_list_view()
        self.assertEqual(response.status_code, 200)


class WorkflowTransitionFieldTestMixin:
    def _create_test_workflow_transition_field(self, extra_data=None):
        kwargs = {
            'field_type': TEST_WORKFLOW_TRANSITION_FIELD_TYPE,
            'name': TEST_WORKFLOW_TRANSITION_FIELD_NAME,
            'label': TEST_WORKFLOW_TRANSITION_FIELD_LABEL,
            'help_text': TEST_WORKFLOW_TRANSITION_FIELD_HELP_TEXT
        }
        kwargs.update(extra_data or {})

        self.test_workflow_transition_field = self.test_workflow_transition.fields.create(
            **kwargs
        )


class WorkflowTransitionFieldViewTestCase(
    WorkflowTestMixin, WorkflowTransitionFieldTestMixin,
    WorkflowTransitionFieldViewTestMixin, WorkflowTransitionViewTestMixin,
    GenericViewTestCase
):
    def setUp(self):
        super(WorkflowTransitionFieldViewTestCase, self).setUp()
        self._create_test_workflow()
        self._create_test_workflow_states()
        self._create_test_workflow_transition()

    def test_workflow_transition_field_list_view_no_permission(self):
        self._create_test_workflow_transition_field()

        response = self._request_test_workflow_transition_field_list_view()
        self.assertNotContains(
            response=response,
            text=self.test_workflow_transition_field.label,
            status_code=404
        )

    def test_workflow_transition_field_list_view_with_access(self):
        self._create_test_workflow_transition_field()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_edit
        )

        response = self._request_test_workflow_transition_field_list_view()
        self.assertContains(
            response=response,
            text=self.test_workflow_transition_field.label,
            status_code=200
        )

    def test_workflow_transition_field_create_view_no_permission(self):
        workflow_transition_field_count = self.test_workflow_transition.fields.count()

        response = self._request_workflow_transition_field_create_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            self.test_workflow_transition.fields.count(),
            workflow_transition_field_count
        )

    def test_workflow_transition_field_create_view_with_access(self):
        workflow_transition_field_count = self.test_workflow_transition.fields.count()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_edit
        )

        response = self._request_workflow_transition_field_create_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self.test_workflow_transition.fields.count(),
            workflow_transition_field_count + 1
        )

    def test_workflow_transition_field_delete_view_no_permission(self):
        self._create_test_workflow_transition_field()

        workflow_transition_field_count = self.test_workflow_transition.fields.count()

        response = self._request_workflow_transition_field_delete_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            self.test_workflow_transition.fields.count(),
            workflow_transition_field_count
        )

    def test_workflow_transition_field_delete_view_with_access(self):
        self._create_test_workflow_transition_field()

        workflow_transition_field_count = self.test_workflow_transition.fields.count()

        self.grant_access(
            obj=self.test_workflow, permission=permission_workflow_edit
        )

        response = self._request_workflow_transition_field_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self.test_workflow_transition.fields.count(),
            workflow_transition_field_count - 1
        )


class WorkflowInstanceTransitionFieldViewTestCase(
    WorkflowTestMixin, WorkflowTransitionFieldTestMixin,
    WorkflowTransitionFieldViewTestMixin, WorkflowTransitionViewTestMixin,
    GenericDocumentViewTestCase
):
    def setUp(self):
        super().setUp()
        self._create_test_workflow(add_document_type=True)
        self._create_test_workflow_states()
        self._create_test_workflow_transition()
        self._create_test_workflow_transition_field(
            extra_data={
                'widget': WIDGET_CLASS_TEXTAREA
            }
        )
        self._upload_test_document()
        self.test_workflow_instance = self.test_document.workflows.first()

    def test_workflow_transition_text_area_widget_execute_view_with_transition_access(self):
        self.grant_access(
            obj=self.test_workflow_transition,
            permission=permission_workflow_transition
        )

        response = self._request_test_workflow_transition_execute_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self.test_workflow_instance.get_current_state(),
            self.test_workflow_state_2
        )
