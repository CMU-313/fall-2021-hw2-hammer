from __future__ import unicode_literals

from common.tests import BaseTestCase

from .mixins import UserTestMixin


class UserTestCase(UserTestMixin, BaseTestCase):
    def test_natural_keys(self):
        self._create_user()
        self._test_database_conversion('auth', 'user_management')
