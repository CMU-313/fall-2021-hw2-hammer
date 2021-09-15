from __future__ import unicode_literals

from django.test import TestCase
from django.urls import reverse

from mayan.apps.common.settings import setting_home_view
from mayan.apps.common.tests.utils import mute_stdout

from ..models import AutoAdminSingleton

from .literals import TEST_FIRST_TIME_LOGIN_TEXT, TEST_MOCK_VIEW_TEXT


class AutoAdminViewCase(TestCase):
    def setUp(self):
        with mute_stdout():
            AutoAdminSingleton.objects.create_autoadmin()

    def _request_home_view(self):
        return self.client.get(
            reverse(setting_home_view.value), follow=True
        )

    def test_login_302_view(self):
        response = self._request_home_view()

        self.assertContains(
            response=response, text=TEST_FIRST_TIME_LOGIN_TEXT,
            status_code=200
        )

    def test_login_ok_view(self):
        autoadmin = AutoAdminSingleton.objects.get()
        logged_in = self.client.login(
            username=autoadmin.account,
            password=autoadmin.password
        )
        self.assertTrue(logged_in)

        response = self._request_home_view()

        self.assertNotContains(
            response=response, text=TEST_MOCK_VIEW_TEXT,
            status_code=200
        )
