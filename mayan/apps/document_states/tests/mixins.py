from ..classes import WorkflowAction
from ..models import Workflow, WorkflowRuntimeProxy, WorkflowStateRuntimeProxy

from .literals import (
    DOCUMENT_WORKFLOW_LAUNCH_ACTION_CLASS_PATH,
    TEST_WORKFLOW_INITIAL_STATE_LABEL, TEST_WORKFLOW_INITIAL_STATE_COMPLETION,
    TEST_WORKFLOW_INSTANCE_LOG_ENTRY_COMMENT, TEST_WORKFLOW_INTERNAL_NAME,
    TEST_WORKFLOW_LABEL, TEST_WORKFLOW_LABEL_EDITED,
    TEST_WORKFLOW_STATE_ACTION_LABEL, TEST_WORKFLOW_STATE_ACTION_LABEL_EDITED,
    TEST_WORKFLOW_STATE_ACTION_DOTTED_PATH, TEST_WORKFLOW_STATE_ACTION_WHEN,
    TEST_WORKFLOW_STATE_COMPLETION, TEST_WORKFLOW_STATE_LABEL,
    TEST_WORKFLOW_STATE_LABEL_EDITED,
    TEST_WORKFLOW_TRANSITION_FIELD_HELP_TEXT,
    TEST_WORKFLOW_TRANSITION_FIELD_LABEL,
    TEST_WORKFLOW_TRANSITION_FIELD_LABEL_EDITED,
    TEST_WORKFLOW_TRANSITION_FIELD_NAME, TEST_WORKFLOW_TRANSITION_FIELD_TYPE,
    TEST_WORKFLOW_TRANSITION_LABEL, TEST_WORKFLOW_TRANSITION_LABEL_EDITED,
    TEST_WORKFLOW_TRANSITION_LABEL_2
)


class DocumentWorkflowAPIViewTestMixin:
    def _request_test_workflow_instance_detail_api_view(self):
        return self.get(
            viewname='rest_api:workflowinstance-detail', kwargs={
                'pk': self.test_document.pk,
                'workflow_pk': self.test_document.workflows.first().pk
            }
        )

    def _request_test_workflow_instance_list_api_view(self):
        return self.get(
            viewname='rest_api:workflowinstance-list',
            kwargs={'pk': self.test_document.pk}
        )

    def _request_test_workflow_instance_log_entry_create_api_view(self, workflow_instance):
        return self.post(
            viewname='rest_api:workflowinstancelogentry-list', kwargs={
                'pk': self.test_document.pk,
                'workflow_pk': workflow_instance.pk
            }, data={'transition_pk': self.test_workflow_transition.pk}
        )

    def _request_test_workflow_instance_log_entry_list_api_view(self):
        return self.get(
            viewname='rest_api:workflowinstancelogentry-list', kwargs={
                'pk': self.test_document.pk,
                'workflow_pk': self.test_document.workflows.first().pk
            }
        )


class DocumentWorkflowLaunchActionViewTestMixin:
    def _request_document_workflow_launch_action_create_view(self):
        return self.post(
            viewname='document_states:workflow_template_state_action_create',
            kwargs={
                'workflow_template_state_id': self.test_workflow_state.pk,
                'class_path': DOCUMENT_WORKFLOW_LAUNCH_ACTION_CLASS_PATH
            }, data={
                'label': TEST_WORKFLOW_STATE_ACTION_LABEL,
                'when': TEST_WORKFLOW_STATE_ACTION_WHEN,
                'workflows': self.test_workflow.pk
            }
        )


class DocumentWorkflowTemplateViewTestMixin:
    def _request_test_document_single_workflow_launch_view(self):
        return self.post(
            data={'workflows': self.test_workflow.pk},
            kwargs={'document_id': self.test_document.pk},
            viewname='document_states:document_single_workflow_templates_launch'
        )


class TestWorkflowAction(WorkflowAction):
    label = 'test workflow state action'

    def execute(self, context):
        context['workflow_instance']._workflow_state_action_executed = True


class WorkflowRuntimeProxyStateViewTestMixin:
    def _request_test_workflow_runtime_proxy_state_list_view(self):
        return self.get(
            viewname='document_states:workflow_runtime_proxy_state_list',
            kwargs={'workflow_runtime_proxy_id': self.test_workflow.pk}
        )

    def _request_test_workflow_runtime_proxy_state_document_list_view(self):
        return self.get(
            viewname='document_states:workflow_runtime_proxy_state_document_list',
            kwargs={
                'workflow_runtime_proxy_state_id': self.test_workflow_state_1.pk
            }
        )


class WorkflowAPIViewTestMixin:
    def _request_test_document_type_workflow_list_api_view(self):
        return self.get(
            viewname='rest_api:documenttype-workflow-list',
            kwargs={'pk': self.test_document_type.pk}
        )

    def _request_test_workflow_create_api_view(self, extra_data=None):
        data = {
            'internal_name': TEST_WORKFLOW_INTERNAL_NAME,
            'label': TEST_WORKFLOW_LABEL,
        }

        if extra_data:
            data.update(extra_data)

        return self.post(
            viewname='rest_api:workflow-list', data=data
        )

    def _request_test_workflow_delete_api_view(self):
        return self.delete(
            viewname='rest_api:workflow-detail', kwargs={
                'pk': self.test_workflow.pk
            }
        )

    def _request_test_workflow_detail_api_view(self):
        return self.get(
            viewname='rest_api:workflow-detail', kwargs={
                'pk': self.test_workflow.pk
            }
        )

    def _request_test_workflow_document_type_delete_api_view(self):
        return self.delete(
            viewname='rest_api:workflow-document-type-detail',
            kwargs={
                'pk': self.test_workflow.pk,
                'document_type_pk': self.test_document_type.pk
            }
        )

    def _request_test_workflow_document_type_detail_api_view(self):
        return self.get(
            viewname='rest_api:workflow-document-type-detail',
            kwargs={
                'pk': self.test_workflow.pk,
                'document_type_pk': self.test_document_type.pk
            }
        )

    def _request_test_workflow_document_type_list_create_api_view(self):
        return self.post(
            viewname='rest_api:workflow-document-type-list',
            kwargs={'pk': self.test_workflow.pk}, data={
                'document_type_pk': self.test_document_type.pk
            }
        )

    def _request_test_workflow_document_type_list_api_view(self):
        return self.get(
            viewname='rest_api:workflow-document-type-list', kwargs={
                'pk': self.test_workflow.pk
            }
        )

    def _request_test_workflow_edit_patch_view(self):
        return self.patch(
            viewname='rest_api:workflow-detail', kwargs={
                'pk': self.test_workflow.pk
            }, data={'label': TEST_WORKFLOW_LABEL_EDITED}
        )

    def _request_test_workflow_edit_put_view(self):
        return self.put(
            viewname='rest_api:workflow-detail', kwargs={
                'pk': self.test_workflow.pk
            }, data={
                'internal_name': TEST_WORKFLOW_INTERNAL_NAME,
                'label': TEST_WORKFLOW_LABEL_EDITED
            }
        )

    def _request_test_workflow_list_api_view(self):
        return self.get(viewname='rest_api:workflow-list')


class WorkflowRuntimeProxyViewTestMixin:
    def _request_test_workflow_runtime_proxy_list_view(self):
        return self.get(
            viewname='document_states:workflow_runtime_proxy_list'
        )

    def _request_test_workflow_runtime_proxy_document_list_view(self):
        return self.get(
            viewname='document_states:workflow_runtime_proxy_document_list',
            kwargs={'workflow_runtime_proxy_id': self.test_workflow.pk}
        )


class WorkflowStateActionTestMixin:
    TestWorkflowAction = TestWorkflowAction
    test_workflow_state_action_path = 'mayan.apps.document_states.tests.mixins.TestWorkflowAction'

    def _create_test_workflow_state_action(self, workflow_state_index=0):
        self.test_workflow_state_action = self.test_workflow_states[
            workflow_state_index
        ].actions.create(
            label=self.TestWorkflowAction.label,
            action_path=self.test_workflow_state_action_path
        )


class WorkflowStateActionViewTestMixin:
    def _request_test_workflow_template_state_action_create_get_view(self, class_path):
        return self.get(
            viewname='document_states:workflow_template_state_action_create',
            kwargs={
                'workflow_template_state_id': self.test_workflow_state.pk,
                'class_path': class_path
            }
        )

    def _request_test_workflow_template_state_action_create_post_view(
        self, class_path, extra_data=None
    ):
        data = {
            'label': TEST_WORKFLOW_STATE_ACTION_LABEL,
            'when': TEST_WORKFLOW_STATE_ACTION_WHEN
        }
        if extra_data:
            data.update(extra_data)

        return self.post(
            viewname='document_states:workflow_template_state_action_create',
            kwargs={
                'workflow_template_state_id': self.test_workflow_state.pk,
                'class_path': class_path
            }, data=data
        )

    def _request_test_worflow_template_state_action_delete_view(self):
        return self.post(
            viewname='document_states:workflow_template_state_action_delete',
            kwargs={
                'workflow_template_state_action_id': self.test_workflow_state_action.pk
            }
        )

    def _request_test_worflow_template_state_action_edit_view(self):
        return self.post(
            viewname='document_states:workflow_template_state_action_edit',
            kwargs={
                'workflow_template_state_action_id': self.test_workflow_state_action.pk
            }, data={
                'label': TEST_WORKFLOW_STATE_ACTION_LABEL_EDITED,
                'when': self.test_workflow_state_action.when
            }
        )

    def _request_test_worflow_template_state_action_list_view(self):
        return self.get(
            viewname='document_states:workflow_template_state_action_list',
            kwargs={'workflow_template_state_id': self.test_workflow_state.pk}
        )

    def _request_test_workflow_state_action_selection_view(self):
        return self.post(
            viewname='document_states:workflow_template_state_action_selection',
            kwargs={
                'workflow_template_state_id': self.test_workflow_state.pk
            }, data={'klass': TEST_WORKFLOW_STATE_ACTION_DOTTED_PATH}
        )


class WorkflowStateAPIViewTestMixin:
    def _request_test_workflow_state_create_api_view(self):
        return self.post(
            viewname='rest_api:workflowstate-list',
            kwargs={'pk': self.test_workflow.pk}, data={
                'completion': TEST_WORKFLOW_STATE_COMPLETION,
                'label': TEST_WORKFLOW_STATE_LABEL
            }
        )

    def _request_test_workflow_state_delete_api_view(self):
        return self.delete(
            viewname='rest_api:workflowstate-detail',
            kwargs={
                'pk': self.test_workflow.pk,
                'state_pk': self.test_workflow_state.pk
            }
        )

    def _request_test_workflow_state_detail_api_view(self):
        return self.get(
            viewname='rest_api:workflowstate-detail',
            kwargs={
                'pk': self.test_workflow.pk,
                'state_pk': self.test_workflow_state.pk
            }
        )

    def _request_test_workflow_state_list_api_view(self):
        return self.get(
            viewname='rest_api:workflowstate-list', kwargs={
                'pk': self.test_workflow.pk
            }
        )

    def _request_test_workflow_state_edit_patch_api_view(self):
        return self.patch(
            viewname='rest_api:workflowstate-detail',
            kwargs={
                'pk': self.test_workflow.pk,
                'state_pk': self.test_workflow_state.pk
            }, data={
                'label': TEST_WORKFLOW_STATE_LABEL_EDITED
            }
        )

    def _request_test_workflow_state_edit_put_api_view(self):
        return self.put(
            viewname='rest_api:workflowstate-detail',
            kwargs={
                'pk': self.test_workflow.pk,
                'state_pk': self.test_workflow_state.pk
            }, data={
                'label': TEST_WORKFLOW_STATE_LABEL_EDITED
            }
        )


class WorkflowStateViewTestMixin:
    def _request_test_workflow_state_create_view(self, extra_data=None):
        data = {
            'label': TEST_WORKFLOW_STATE_LABEL,
            'completion': TEST_WORKFLOW_STATE_COMPLETION,
        }
        if extra_data:
            data.update(extra_data)

        return self.post(
            viewname='document_states:workflow_template_state_create',
            kwargs={'workflow_template_id': self.test_workflow.pk}, data=data
        )

    def _request_test_workflow_state_delete_view(self):
        return self.post(
            viewname='document_states:workflow_template_state_delete',
            kwargs={
                'workflow_template_state_id': self.test_workflow_state_1.pk
            }
        )

    def _request_test_workflow_state_edit_view(self):
        return self.post(
            viewname='document_states:workflow_template_state_edit',
            kwargs={
                'workflow_template_state_id': self.test_workflow_state_1.pk
            }, data={
                'label': TEST_WORKFLOW_STATE_LABEL_EDITED
            }
        )

    def _request_test_workflow_state_list_view(self):
        return self.get(
            viewname='document_states:workflow_template_state_list',
            kwargs={'workflow_template_id': self.test_workflow.pk}
        )


class WorkflowTestMixin:
    def _create_test_workflow(self, add_document_type=False, auto_launch=True):
        self.test_workflow = Workflow.objects.create(
            auto_launch=auto_launch, label=TEST_WORKFLOW_LABEL,
            internal_name=TEST_WORKFLOW_INTERNAL_NAME
        )
        self.test_workflow_runtime_proxy = WorkflowRuntimeProxy.objects.get(
            pk=self.test_workflow.pk
        )

        if add_document_type:
            self.test_workflow.document_types.add(self.test_document_type)

    def _create_test_workflow_state(self):
        self.test_workflow_states = []
        self.test_workflow_state = self.test_workflow.states.create(
            completion=TEST_WORKFLOW_STATE_COMPLETION, initial=True,
            label=TEST_WORKFLOW_STATE_LABEL
        )
        self.test_workflow_states.append(self.test_workflow_state)
        self.test_workflow_state_runtime_proxy = WorkflowStateRuntimeProxy.objects.get(
            pk=self.test_workflow_state.pk
        )

    def _create_test_workflow_states(self):
        self.test_workflow_states = []
        self.test_workflow_state_1 = self.test_workflow.states.create(
            completion=TEST_WORKFLOW_INITIAL_STATE_COMPLETION,
            initial=True, label=TEST_WORKFLOW_INITIAL_STATE_LABEL
        )
        self.test_workflow_states.append(self.test_workflow_state_1)
        self.test_workflow_state_2 = self.test_workflow.states.create(
            completion=TEST_WORKFLOW_STATE_COMPLETION,
            label=TEST_WORKFLOW_STATE_LABEL
        )
        self.test_workflow_states.append(self.test_workflow_state_2)
        self.test_workflow_state_runtime_proxy_1 = WorkflowStateRuntimeProxy.objects.get(
            pk=self.test_workflow_state_1.pk
        )
        self.test_workflow_state_runtime_proxy_2 = WorkflowStateRuntimeProxy.objects.get(
            pk=self.test_workflow_state_2.pk
        )

    def _create_test_workflow_transition(self):
        self.test_workflow_transition = self.test_workflow.transitions.create(
            label=TEST_WORKFLOW_TRANSITION_LABEL,
            origin_state=self.test_workflow_state_1,
            destination_state=self.test_workflow_state_2,
        )

    def _create_test_workflow_transitions(self):
        self.test_workflow_transition = self.test_workflow.transitions.create(
            workflow=self.test_workflow, label=TEST_WORKFLOW_TRANSITION_LABEL,
            origin_state=self.test_workflow_state_1,
            destination_state=self.test_workflow_state_2
        )

        self.test_workflow_transition_2 = self.test_workflow.transitions.create(
            workflow=self.test_workflow, label=TEST_WORKFLOW_TRANSITION_LABEL_2,
            origin_state=self.test_workflow_state_1,
            destination_state=self.test_workflow_state_2
        )

    def _create_test_workflow_instance_log_entry(self):
        self.test_document.workflows.first().log_entries.create(
            comment=TEST_WORKFLOW_INSTANCE_LOG_ENTRY_COMMENT,
            transition=self.test_workflow_transition,
            user=self._test_case_user
        )

    def _transition_test_workflow_instance(self, extra_data=None):
        self.test_document.workflows.first().do_transition(
            comment=TEST_WORKFLOW_INSTANCE_LOG_ENTRY_COMMENT,
            extra_data=extra_data, transition=self.test_workflow_transition,
            user=self._test_case_user
        )


class WorkflowToolViewTestMixin:
    def _request_workflow_launch_view(self):
        return self.post(
            viewname='document_states:tool_launch_workflows',
        )


class WorkflowTransitionEventViewTestMixin:
    def _request_test_workflow_transition_event_list_view(self):
        return self.get(
            viewname='document_states:workflow_template_transition_events',
            kwargs={
                'workflow_template_transition_id': self.test_workflow_transition.pk
            }
        )


class WorkflowTransitionFieldViewTestMixin:
    def _request_workflow_transition_field_create_view(self):
        return self.post(
            viewname='document_states:workflow_template_transition_field_create',
            kwargs={
                'workflow_template_transition_id': self.test_workflow_transition.pk
            }, data={
                'field_type': TEST_WORKFLOW_TRANSITION_FIELD_TYPE,
                'name': TEST_WORKFLOW_TRANSITION_FIELD_NAME,
                'label': TEST_WORKFLOW_TRANSITION_FIELD_LABEL,
                'help_text': TEST_WORKFLOW_TRANSITION_FIELD_HELP_TEXT
            }
        )

    def _request_workflow_transition_field_delete_view(self):
        return self.post(
            viewname='document_states:workflow_template_transition_field_delete',
            kwargs={
                'workflow_template_transition_field_id': self.test_workflow_transition_field.pk
            },
        )

    def _request_workflow_transition_field_edit_view(self):
        return self.post(
            viewname='document_states:workflow_template_transition_field_edit',
            kwargs={
                'workflow_template_transition_field_id': self.test_workflow_transition_field.pk
            }, data={
                'field_type': TEST_WORKFLOW_TRANSITION_FIELD_TYPE,
                'name': TEST_WORKFLOW_TRANSITION_FIELD_NAME,
                'label': TEST_WORKFLOW_TRANSITION_FIELD_LABEL_EDITED,
                'help_text': TEST_WORKFLOW_TRANSITION_FIELD_HELP_TEXT
            }
        )

    def _request_test_workflow_transition_field_list_view(self):
        return self.get(
            viewname='document_states:workflow_template_transition_field_list',
            kwargs={
                'workflow_template_transition_id': self.test_workflow_transition.pk
            }
        )


class WorkflowTransitionAPIViewTestMixin:
    def _request_test_workflow_transition_create_api_view(self):
        return self.post(
            viewname='rest_api:workflowtransition-list',
            kwargs={'pk': self.test_workflow.pk}, data={
                'label': TEST_WORKFLOW_TRANSITION_LABEL,
                'origin_state_pk': self.test_workflow_state_1.pk,
                'destination_state_pk': self.test_workflow_state_2.pk,
            }
        )

    def _request_test_workflow_transition_delete_api_view(self):
        return self.delete(
            viewname='rest_api:workflowtransition-detail',
            kwargs={
                'pk': self.test_workflow.pk,
                'transition_pk': self.test_workflow_transition.pk
            }
        )

    def _request_test_workflow_transition_detail_api_view(self):
        return self.get(
            viewname='rest_api:workflowtransition-detail',
            kwargs={
                'pk': self.test_workflow.pk,
                'transition_pk': self.test_workflow_transition.pk
            }
        )

    def _request_test_workflow_transition_list_api_view(self):
        return self.get(
            viewname='rest_api:workflowtransition-list',
            kwargs={'pk': self.test_workflow.pk}
        )

    def _request_test_workflow_transition_edit_patch_api_view(self):
        return self.patch(
            viewname='rest_api:workflowtransition-detail',
            kwargs={
                'pk': self.test_workflow.pk,
                'transition_pk': self.test_workflow_transition.pk
            }, data={
                'label': TEST_WORKFLOW_TRANSITION_LABEL_EDITED,
                'origin_state_pk': self.test_workflow_state_2.pk,
                'destination_state_pk': self.test_workflow_state_1.pk,
            }
        )

    def _request_test_workflow_transition_edit_put_api_view_via(self):
        return self.put(
            viewname='rest_api:workflowtransition-detail',
            kwargs={
                'pk': self.test_workflow.pk,
                'transition_pk': self.test_workflow_transition.pk
            }, data={
                'label': TEST_WORKFLOW_TRANSITION_LABEL_EDITED,
                'origin_state_pk': self.test_workflow_state_2.pk,
                'destination_state_pk': self.test_workflow_state_1.pk,
            }
        )


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


class WorkflowTransitionViewTestMixin:
    def _request_test_workflow_transition_create_view(self):
        return self.post(
            viewname='document_states:workflow_template_transition_create',
            kwargs={'workflow_template_id': self.test_workflow.pk}, data={
                'label': TEST_WORKFLOW_TRANSITION_LABEL,
                'origin_state': self.test_workflow_state_1.pk,
                'destination_state': self.test_workflow_state_2.pk,
            }
        )

    def _request_test_workflow_transition_delete_view(self):
        return self.post(
            viewname='document_states:workflow_template_transition_delete',
            kwargs={
                'workflow_template_transition_id': self.test_workflow_transition.pk
            }
        )

    def _request_test_workflow_transition_edit_view(self):
        return self.post(
            viewname='document_states:workflow_template_transition_edit',
            kwargs={
                'workflow_template_transition_id': self.test_workflow_transition.pk
            }, data={
                'label': TEST_WORKFLOW_TRANSITION_LABEL_EDITED,
                'origin_state': self.test_workflow_state_1.pk,
                'destination_state': self.test_workflow_state_2.pk,
            }
        )

    def _request_test_workflow_transition_execute_view(self):
        return self.post(
            viewname='document_states:workflow_instance_transition_execute',
            kwargs={
                'workflow_instance_id': self.test_workflow_instance.pk,
                'workflow_transition_id': self.test_workflow_transition.pk,
            }
        )

    def _request_test_workflow_transition_list_view(self):
        return self.get(
            viewname='document_states:workflow_template_transition_list',
            kwargs={'workflow_template_id': self.test_workflow.pk}
        )

    def _request_test_workflow_transition_selection_get_view(self):
        return self.get(
            viewname='document_states:workflow_instance_transition_selection',
            kwargs={
                'workflow_instance_id': self.test_workflow_instance.pk,
            }
        )

    def _request_test_workflow_transition_selection_post_view(self):
        return self.post(
            viewname='document_states:workflow_instance_transition_selection',
            kwargs={
                'workflow_instance_id': self.test_workflow_instance.pk,
            }, data={
                'transition': self.test_workflow_transition.pk,
            }
        )


class WorkflowViewTestMixin:
    def _request_test_workflow_create_view(self):
        return self.post(
            viewname='document_states:workflow_template_create', data={
                'label': TEST_WORKFLOW_LABEL,
                'internal_name': TEST_WORKFLOW_INTERNAL_NAME,
            }
        )

    def _request_test_workflow_delete_view(self):
        return self.post(
            viewname='document_states:workflow_template_single_delete', kwargs={
                'workflow_template_id': self.test_workflow.pk
            }
        )

    def _request_test_workflow_edit_view(self):
        return self.post(
            viewname='document_states:workflow_template_edit', kwargs={
                'workflow_template_id': self.test_workflow.pk,
            }, data={
                'label': TEST_WORKFLOW_LABEL_EDITED,
                'internal_name': self.test_workflow.internal_name
            }
        )

    def _request_test_workflow_launch_view(self):
        return self.post(
            viewname='document_states:workflow_template_launch', kwargs={
                'workflow_template_id': self.test_workflow.pk
            }
        )

    def _request_test_workflow_list_view(self):
        return self.get(
            viewname='document_states:workflow_template_list',
        )

    def _request_test_workflow_template_preview_view(self):
        return self.get(
            viewname='document_states:workflow_template_preview', kwargs={
                'workflow_template_id': self.test_workflow.pk,
            }
        )
