from django.contrib.contenttypes.models import ContentType

from mayan.apps.documents.tests.base import GenericDocumentViewTestCase
from mayan.apps.testing.tests.base import GenericViewTestCase

from ..models import Notification
from ..permissions import permission_events_view

from .mixins import (
    EventTypeTestMixin, EventsViewTestMixin, NotificationTestMixin,
    NotificationViewTestMixin, UserEventViewsTestMixin
)


class EventsViewTestCase(
    EventTypeTestMixin, EventsViewTestMixin, GenericDocumentViewTestCase
):
    auto_upload_test_document = False

    def setUp(self):
        super(EventsViewTestCase, self).setUp()
        self._create_test_event_type()
        self._create_test_user()
        self.test_object = self.test_document_type

        content_type = ContentType.objects.get_for_model(model=self.test_object)

        self.view_arguments = {
            'app_label': content_type.app_label,
            'model_name': content_type.model,
            'object_id': self.test_object.pk
        }
        self.test_event_type.commit(
            actor=self.test_user, action_object=self.test_object
        )

    def test_events_for_object_view_no_permission(self):
        response = self._request_events_for_object_view()
        self.assertNotContains(
            response=response, text=self.test_object.label, status_code=404
        )

    def test_events_for_object_view_with_access(self):
        self.grant_access(
            obj=self.test_object, permission=permission_events_view
        )

        response = self._request_events_for_object_view()
        self.assertContains(
            response=response, text=self.test_object.label, status_code=200
        )


class NotificationViewTestCase(
    NotificationTestMixin, NotificationViewTestMixin, GenericViewTestCase
):
    def test_notification_list_view(self):
        response = self._request_test_notification_list_view()
        self.assertEqual(response.status_code, 200)

    def test_notification_mark_read_all_view(self):
        self._create_test_notification()
        notification_count = Notification.objects.get_unread().count()

        response = self._request_test_notification_mark_read_all_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            Notification.objects.get_unread().count(),
            notification_count - 1
        )

    def test_notification_mark_read_view(self):
        self._create_test_notification()
        notification_count = Notification.objects.get_unread().count()

        response = self._request_test_notification_mark_read()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            Notification.objects.get_unread().count(),
            notification_count - 1
        )


class UserEventViewsTestCase(UserEventViewsTestMixin, GenericViewTestCase):
    def test_user_event_type_subscription_list_view(self):
        response = self._request_test_user_event_type_subscription_list_view()
        self.assertEqual(response.status_code, 200)
