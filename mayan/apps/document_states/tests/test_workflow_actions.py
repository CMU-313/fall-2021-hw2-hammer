import json
import mock

from mayan.apps.documents.tests.base import GenericDocumentViewTestCase
from mayan.apps.testing.tests.base import GenericViewTestCase
from mayan.apps.testing.tests.mixins import TestServerTestCaseMixin
from mayan.apps.testing.tests.mocks import request_method_factory

from ..literals import WORKFLOW_ACTION_ON_ENTRY
from ..models import Workflow, WorkflowInstance
from ..permissions import permission_workflow_template_edit
from ..workflow_actions import (
    DocumentPropertiesEditAction, DocumentWorkflowLaunchAction, HTTPAction
)

from .literals import (
    TEST_DOCUMENT_EDIT_WORKFLOW_TEMPLATE_STATE_ACTION_DOTTED_PATH,
    TEST_DOCUMENT_EDIT_WORKFLOW_TEMPLATE_STATE_ACTION_TEXT_LABEL,
    TEST_DOCUMENT_EDIT_WORKFLOW_TEMPLATE_STATE_ACTION_TEXT_DESCRIPTION,
    TEST_DOCUMENT_EDIT_WORKFLOW_TEMPLATE_STATE_ACTION_TEXT_DATA,
    TEST_DOCUMENT_EDIT_WORKFLOW_TEMPLATE_STATE_ACTION_TEMPLATE_DATA,
    TEST_HEADERS_AUTHENTICATION_KEY, TEST_HEADERS_AUTHENTICATION_VALUE,
    TEST_HEADERS_KEY, TEST_HEADERS_JSON, TEST_HEADERS_JSON_TEMPLATE,
    TEST_HEADERS_JSON_TEMPLATE_KEY, TEST_HEADERS_VALUE, TEST_PAYLOAD_JSON,
    TEST_PAYLOAD_TEMPLATE_DOCUMENT_LABEL, TEST_SERVER_USERNAME,
    TEST_SERVER_PASSWORD
)
from .mixins.workflow_template_mixins import WorkflowTemplateTestMixin
from .mixins.workflow_template_state_mixins import (
    WorkflowTemplateStateActionLaunchViewTestMixin,
    WorkflowTemplateStateActionViewTestMixin
)


class HTTPWorkflowActionTestCase(
    TestServerTestCaseMixin, GenericDocumentViewTestCase,
    WorkflowTemplateTestMixin,
):
    auto_upload_test_document = False
    auto_add_test_view = True

    @mock.patch('requests.sessions.Session.get_adapter')
    def test_http_post_action_simple(self, mock_object):
        mock_object.side_effect = request_method_factory(test_case=self)

        action = HTTPAction(
            form_data={
                'method': 'POST',
                'url': self.testserver_url
            }
        )
        action.execute(context={})

        self.assertFalse(self.test_view_request is None)

    @mock.patch('requests.sessions.Session.get_adapter')
    def test_http_post_action_payload_simple(self, mock_object):
        mock_object.side_effect = request_method_factory(test_case=self)

        action = HTTPAction(
            form_data={
                'payload': TEST_PAYLOAD_JSON,
                'url': self.testserver_url,
                'method': 'POST'
            }
        )
        action.execute(context={})

        self.assertEqual(
            json.loads(s=self.test_view_request.body),
            {'label': 'label'}
        )

    @mock.patch('requests.sessions.Session.get_adapter')
    def test_http_post_action_payload_template(self, mock_object):
        self._create_test_document_stub()

        mock_object.side_effect = request_method_factory(test_case=self)

        action = HTTPAction(
            form_data={
                'payload': TEST_PAYLOAD_TEMPLATE_DOCUMENT_LABEL,
                'url': self.testserver_url,
                'method': 'POST'
            }
        )
        action.execute(context={'document': self.test_document})

        self.assertEqual(
            json.loads(s=self.test_view_request.body),
            {'label': self.test_document.label}
        )

    @mock.patch('requests.sessions.Session.get_adapter')
    def test_http_post_action_headers_simple(self, mock_object):
        mock_object.side_effect = request_method_factory(test_case=self)

        action = HTTPAction(
            form_data={
                'headers': TEST_HEADERS_JSON,
                'url': self.testserver_url,
                'method': 'POST'
            }
        )
        action.execute(context={})

        self.assertTrue(
            TEST_HEADERS_KEY in self.test_view_request.META,
        )
        self.assertEqual(
            self.test_view_request.META[TEST_HEADERS_KEY], TEST_HEADERS_VALUE
        )

    @mock.patch('requests.sessions.Session.get_adapter')
    def test_http_post_action_headers_template(self, mock_object):
        self._create_test_document_stub()

        mock_object.side_effect = request_method_factory(test_case=self)

        action = HTTPAction(
            form_data={
                'headers': TEST_HEADERS_JSON_TEMPLATE,
                'url': self.testserver_url,
                'method': 'POST'
            }
        )
        action.execute(context={'document': self.test_document})

        self.assertTrue(
            TEST_HEADERS_JSON_TEMPLATE_KEY in self.test_view_request.META,
        )
        self.assertEqual(
            self.test_view_request.META[TEST_HEADERS_JSON_TEMPLATE_KEY],
            self.test_document.label
        )

    @mock.patch('requests.sessions.Session.get_adapter')
    def test_http_post_action_authentication(self, mock_object):
        mock_object.side_effect = request_method_factory(test_case=self)

        action = HTTPAction(
            form_data={
                'password': TEST_SERVER_PASSWORD,
                'url': self.testserver_url,
                'username': TEST_SERVER_USERNAME,
                'method': 'POST'
            }
        )
        action.execute(context={})

        self.assertTrue(
            TEST_HEADERS_AUTHENTICATION_KEY in self.test_view_request.META,
        )
        self.assertEqual(
            self.test_view_request.META[TEST_HEADERS_AUTHENTICATION_KEY],
            TEST_HEADERS_AUTHENTICATION_VALUE
        )

    @mock.patch('requests.sessions.Session.get_adapter')
    def test_http_post_action_timeout_value_int(self, mock_object):
        mock_object.side_effect = request_method_factory(test_case=self)

        action = HTTPAction(
            form_data={
                'timeout': '1',
                'url': self.testserver_url,
                'method': 'POST'
            }
        )
        action.execute(context={})

        self.assertEqual(self.timeout, 1)

    @mock.patch('requests.sessions.Session.get_adapter')
    def test_http_post_action_timeout_value_float(self, mock_object):
        mock_object.side_effect = request_method_factory(test_case=self)

        action = HTTPAction(
            form_data={
                'timeout': '1.5',
                'url': self.testserver_url,
                'method': 'POST'
            }
        )
        action.execute(context={})

        self.assertEqual(self.timeout, 1.5)

    @mock.patch('requests.sessions.Session.get_adapter')
    def test_http_post_action_timeout_value_none(self, mock_object):
        mock_object.side_effect = request_method_factory(test_case=self)

        action = HTTPAction(
            form_data={
                'url': self.testserver_url,
                'method': 'POST'
            }
        )
        action.execute(context={})

        self.assertEqual(self.timeout, None)


class HTTPWorkflowActionViewTestCase(
    WorkflowTemplateTestMixin, WorkflowTemplateStateActionViewTestMixin,
    GenericViewTestCase
):
    def setUp(self):
        super().setUp()
        self._create_test_workflow_template()
        self._create_test_workflow_template_state()

    def test_http_workflow_state_action_create_post_view_no_permission(self):
        action_count = self.test_workflow_template_state.actions.count()

        response = self._request_test_workflow_template_state_action_create_post_view(
            class_path='mayan.apps.document_states.workflow_actions.HTTPAction',
            extra_data={
                'method': 'POST', 'timeout': 0, 'url': '127.0.0.1'
            }
        )
        self.assertEqual(response.status_code, 404)

        self.test_workflow_template_state.refresh_from_db()
        self.assertEqual(
            self.test_workflow_template_state.actions.count(), action_count
        )

    def test_http_workflow_state_action_create_post_view_with_access(self):
        self.grant_access(
            obj=self.test_workflow_template,
            permission=permission_workflow_template_edit
        )
        action_count = self.test_workflow_template_state.actions.count()

        response = self._request_test_workflow_template_state_action_create_post_view(
            class_path='mayan.apps.document_states.workflow_actions.HTTPAction',
            extra_data={
                'method': 'POST', 'timeout': 0, 'url': '127.0.0.1'
            }
        )
        self.assertEqual(response.status_code, 302)

        self.test_workflow_template_state.refresh_from_db()
        self.assertEqual(
            self.test_workflow_template_state.actions.count(), action_count + 1
        )


class DocumentPropertiesEditActionTestCase(
    WorkflowTemplateTestMixin, GenericDocumentViewTestCase
):
    auto_upload_test_document = False

    def test_document_properties_edit_action_field_literals(self):
        self._create_test_document_stub()

        action = DocumentPropertiesEditAction(
            form_data=TEST_DOCUMENT_EDIT_WORKFLOW_TEMPLATE_STATE_ACTION_TEXT_DATA
        )

        test_values = self._model_instance_to_dictionary(
            instance=self.test_document
        )

        action.execute(context={'document': self.test_document})
        self.test_document.refresh_from_db()

        self.assertNotEqual(
            test_values, self._model_instance_to_dictionary(
                instance=self.test_document
            )
        )

    def test_document_properties_edit_action_field_templates(self):
        self._create_test_document_stub()

        label = self.test_document.label

        action = DocumentPropertiesEditAction(
            form_data=TEST_DOCUMENT_EDIT_WORKFLOW_TEMPLATE_STATE_ACTION_TEMPLATE_DATA
        )
        action.execute(context={'document': self.test_document})

        self.assertEqual(
            self.test_document.label,
            '{} new'.format(label)
        )
        self.assertEqual(
            self.test_document.description,
            label
        )

    def test_document_properties_edit_action_workflow_execute(self):
        self._create_test_workflow_template()
        self._create_test_workflow_template_state()
        self._create_test_workflow_template_state()
        self._create_test_workflow_template_transition()
        self._create_test_workflow_template_transition()

        self.test_workflow_template_states[1].actions.create(
            action_data=json.dumps(
                obj=TEST_DOCUMENT_EDIT_WORKFLOW_TEMPLATE_STATE_ACTION_TEXT_DATA
            ),
            action_path=TEST_DOCUMENT_EDIT_WORKFLOW_TEMPLATE_STATE_ACTION_DOTTED_PATH,
            label='', when=WORKFLOW_ACTION_ON_ENTRY,
        )
        self.test_workflow_template.document_types.add(
            self.test_document_type
        )

        self._create_test_document_stub()

        test_workflow_instance = self.test_document.workflows.first()
        test_workflow_instance.do_transition(
            transition=self.test_workflow_template_transition
        )

        self.assertEqual(
            self.test_document.label,
            TEST_DOCUMENT_EDIT_WORKFLOW_TEMPLATE_STATE_ACTION_TEXT_LABEL
        )
        self.assertEqual(
            self.test_document.description,
            TEST_DOCUMENT_EDIT_WORKFLOW_TEMPLATE_STATE_ACTION_TEXT_DESCRIPTION
        )


class DocumentWorkflowLaunchActionTestCase(
    WorkflowTemplateTestMixin, GenericDocumentViewTestCase
):
    auto_upload_test_document = False

    def test_document_workflow_launch_action(self):
        self._create_test_workflow_template(
            add_test_document_type=True, auto_launch=False
        )
        self._create_test_workflow_template_state()

        self._create_test_document_stub()

        action = DocumentWorkflowLaunchAction(
            form_data={'workflows': Workflow.objects.all()}
        )

        workflow_count = self.test_document.workflows.count()

        action.execute(context={'document': self.test_document})

        self.assertTrue(
            self.test_document.workflows.count(), workflow_count + 1
        )


class DocumentWorkflowLaunchActionViewTestCase(
    WorkflowTemplateStateActionLaunchViewTestMixin,
    WorkflowTemplateTestMixin, GenericDocumentViewTestCase
):
    auto_upload_test_document = False

    def test_document_workflow_launch_action_view_with_full_access(self):
        self._create_test_workflow_template(
            add_test_document_type=True, auto_launch=False
        )

        self._create_test_workflow_template(
            add_test_document_type=True, auto_launch=False
        )
        self._create_test_workflow_template_state()

        self.grant_access(
            obj=self.test_workflow_template,
            permission=permission_workflow_template_edit
        )

        action_count = self.test_workflow_template_state.actions.count()

        response = self._request_document_workflow_template_launch_action_create_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self.test_workflow_template_state.actions.count(),
            action_count + 1
        )

    def test_document_workflow_launch_action_view_and_document_create_with_full_access(self):
        self._create_test_workflow_template(
            add_test_document_type=True, auto_launch=False
        )

        self._create_test_workflow_template(
            add_test_document_type=True, auto_launch=True
        )
        self._create_test_workflow_template_state()

        self.grant_access(
            obj=self.test_workflow_template,
            permission=permission_workflow_template_edit
        )

        action_count = self.test_workflow_template_state.actions.count()
        workflow_instance_count = WorkflowInstance.objects.count()

        response = self._request_document_workflow_template_launch_action_create_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self.test_workflow_template_state.actions.count(),
            action_count + 1
        )

        self._create_test_document_stub()

        self.assertEqual(
            WorkflowInstance.objects.count(), workflow_instance_count + 2
        )
