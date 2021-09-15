from __future__ import absolute_import, unicode_literals

from django.test import TestCase
from django_downloadview import assert_download_response

from mayan.apps.acls.tests.mixins import ACLTestCaseMixin
from mayan.apps.permissions.classes import Permission
from mayan.apps.smart_settings.classes import Namespace

from .mixins import (
    ClientMethodsTestCaseMixin, ContentTypeCheckMixin, DatabaseConversionMixin,
    OpenFileCheckTestCaseMixin, RandomPrimaryKeyModelMonkeyPatchMixin,
    TempfileCheckTestCaseMixin, TestViewTestCaseMixin
)


class BaseTestCase(RandomPrimaryKeyModelMonkeyPatchMixin, DatabaseConversionMixin, ACLTestCaseMixin, OpenFileCheckTestCaseMixin, TempfileCheckTestCaseMixin, TestCase):
    """
    This is the most basic test case class any test in the project should use.
    """
    assert_download_response = assert_download_response

    def setUp(self):
        super(BaseTestCase, self).setUp()
        Namespace.invalidate_cache_all()
        Permission.invalidate_cache()


class GenericViewTestCase(ClientMethodsTestCaseMixin, ContentTypeCheckMixin, TestViewTestCaseMixin, BaseTestCase):
    """
    A generic view test case built on top of the base test case providing
    a single, user customizable view to test object resolution and shorthand
    HTTP method functions.
    """
