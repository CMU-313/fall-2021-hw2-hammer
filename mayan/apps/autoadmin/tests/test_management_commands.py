from django.contrib.auth import get_user_model
from django.core import management

from mayan.apps.testing.tests.base import BaseTestCase
from mayan.apps.testing.tests.utils import mute_stdout

from ..models import AutoAdminSingleton


class AutoAdminManagementCommandTestCase(BaseTestCase):
    create_test_case_user = False

    def setUp(self):
        super().setUp()
        with mute_stdout():
            management.call_command('createautoadmin')

    def tearDown(self):
        AutoAdminSingleton.objects.all().delete()
        super().tearDown()

    def test_autoadmin_creation(self):
        autoadmin = AutoAdminSingleton.objects.get()
        user = get_user_model().objects.first()

        self.assertEqual(AutoAdminSingleton.objects.count(), 1)

        self.assertEqual(autoadmin.account, user)
        self.assertEqual(autoadmin.account.email, user.email)
        self.assertEqual(autoadmin.password_hash, user.password)
