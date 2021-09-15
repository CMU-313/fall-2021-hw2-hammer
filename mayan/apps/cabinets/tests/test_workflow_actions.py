from __future__ import unicode_literals

from mayan.apps.common.tests.base import GenericViewTestCase
from mayan.apps.document_states.tests.base import ActionTestCase
from mayan.apps.document_states.tests.mixins import WorkflowTestMixin

from ..models import Cabinet
from ..workflow_actions import CabinetAddAction, CabinetRemoveAction

from .mixins import CabinetTestMixin


class CabinetWorkflowActionTestCase(CabinetTestMixin, ActionTestCase):
    def setUp(self):
        super(CabinetWorkflowActionTestCase, self).setUp()
        self._create_test_cabinet()

    def test_cabinet_add_action(self):
        action = CabinetAddAction(
            form_data={'cabinets': Cabinet.objects.all()}
        )
        action.execute(context={'document': self.test_document})

        self.assertTrue(
            self.test_document in self.test_cabinet.documents.all()
        )

    def test_cabinet_remove_action(self):
        self.test_cabinet.document_add(document=self.test_document)

        action = CabinetRemoveAction(
            form_data={'cabinets': Cabinet.objects.all()}
        )
        action.execute(context={'document': self.test_document})

        self.assertFalse(
            self.test_document in self.test_cabinet.documents.all()
        )


class CabinetWorkflowActionViewTestCase(
    CabinetTestMixin, WorkflowTestMixin, GenericViewTestCase
):
    def _request_test_workflow_template_state_cabinet_add_action_get_view(self):
        return self.get(
            viewname='document_states:workflow_template_state_action_create',
            kwargs={
                'pk': self.test_workflow_state.pk,
                'class_path': 'mayan.apps.cabinets.workflow_actions.CabinetAddAction'
            }
        )

    def _request_test_workflow_template_state_cabinet_remove_action_get_view(self):
        return self.get(
            viewname='document_states:workflow_template_state_action_create',
            kwargs={
                'pk': self.test_workflow_state.pk,
                'class_path': 'mayan.apps.cabinets.workflow_actions.CabinetRemoveAction'
            }
        )

    def test_cabinet_add_action_create_get_view(self):
        self._create_test_workflow()
        self._create_test_workflow_state()

        response = self._request_test_workflow_template_state_cabinet_add_action_get_view()

        self.assertEqual(response.status_code, 200)

    def test_cabinet_remove_action_create_get_view(self):
        self._create_test_workflow()
        self._create_test_workflow_state()
        self._create_test_cabinet()

        response = self._request_test_workflow_template_state_cabinet_remove_action_get_view()

        self.assertEqual(response.status_code, 200)
