from mayan.apps.common.tests.mixins import ObjectCopyTestMixin
from mayan.apps.documents.tests.mixins.document_mixins import DocumentTestMixin
from mayan.apps.testing.tests.base import BaseTestCase

from .mixins import CabinetTestMixin


class CabinetCopyTestCase(
    CabinetTestMixin, DocumentTestMixin, ObjectCopyTestMixin, BaseTestCase
):
    _test_copy_method = 'get_family'
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self._create_test_document_stub()
        self._create_test_cabinet()
        self._create_test_cabinet_child()
        self.test_cabinet.documents.add(self.test_document)
        self.test_object = self.test_cabinet
