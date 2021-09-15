from __future__ import absolute_import, unicode_literals

from django.contrib.contenttypes.models import ContentType

from mayan.apps.documents.tests import GenericDocumentViewTestCase

from ..permissions import permission_events_view


class EventsViewTestCase(GenericDocumentViewTestCase):
    def setUp(self):
        super(EventsViewTestCase, self).setUp()
        self.test_object = self.document

        content_type = ContentType.objects.get_for_model(model=self.test_object)

        self.view_arguments = {
            'app_label': content_type.app_label,
            'model': content_type.model,
            'object_id': self.test_object.pk
        }

    def _request_events_for_object_view(self):
        return self.get(
            viewname='events:events_for_object', kwargs=self.view_arguments
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
