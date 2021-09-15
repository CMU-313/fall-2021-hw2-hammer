from __future__ import unicode_literals

from actstream.models import Action

from mayan.apps.documents.tests import GenericDocumentViewTestCase

from ..events import event_tag_created, event_tag_edited
from ..models import Tag
from ..permissions import permission_tag_create, permission_tag_edit

from .mixins import TagTestMixin


#TODO: Add tests for event_tag_remove and event_tag_attach
class TagEventsTestCase(TagTestMixin, GenericDocumentViewTestCase):
    def setUp(self):
        super(TagEventsTestCase, self).setUp()
        self.login_user()

    def test_tag_create_event_no_permissions(self):
        Action.objects.all().delete()

        response = self._request_tag_create_view()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Action.objects.count(), 0)

    def test_tag_create_event_with_permissions(self):
        Action.objects.all().delete()

        self.grant_permission(permission=permission_tag_create)

        response = self._request_tag_create_view()

        self.assertEqual(response.status_code, 302)

        event = Action.objects.first()

        tag = Tag.objects.first()

        self.assertEqual(event.verb, event_tag_created.id)
        self.assertEqual(event.target, tag)
        self.assertEqual(event.actor, self._test_case_user)

    def test_tag_edit_event_no_permissions(self):
        self._create_test_tag()
        Action.objects.all().delete()

        response = self._request_tag_edit_view()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Action.objects.count(), 0)

    def test_tag_edit_event_with_access(self):
        self._create_test_tag()
        Action.objects.all().delete()

        self.grant_access(
            permission=permission_tag_edit, obj=self.test_tag
        )

        response = self._request_tag_edit_view()

        self.assertEqual(response.status_code, 302)

        event = Action.objects.first()

        self.assertEqual(event.verb, event_tag_edited.id)
        self.assertEqual(event.target, self.test_tag)
        self.assertEqual(event.actor, self._test_case_user)
