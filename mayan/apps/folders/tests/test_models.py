from __future__ import unicode_literals

from django.test import TestCase, override_settings

from documents.models import DocumentType
from documents.tests import TEST_DOCUMENT_PATH, TEST_DOCUMENT_TYPE

from ..models import Folder

from .literals import TEST_FOLDER_LABEL


@override_settings(OCR_AUTO_OCR=False)
class FolderTestCase(TestCase):
    def setUp(self):
        self.document_type = DocumentType.objects.create(
            label=TEST_DOCUMENT_TYPE
        )

        with open(TEST_DOCUMENT_PATH) as file_object:
            self.document = self.document_type.new_document(
                file_object=file_object
            )

    def tearDown(self):
        self.document_type.delete()

    def test_folder_creation(self):
        folder = Folder.objects.create(label=TEST_FOLDER_LABEL)

        self.assertEqual(Folder.objects.all().count(), 1)
        self.assertEqual(list(Folder.objects.all()), [folder])

    def test_addition_of_documents(self):
        folder = Folder.objects.create(label=TEST_FOLDER_LABEL)
        folder.documents.add(self.document)

        self.assertEqual(folder.documents.count(), 1)
        self.assertEqual(list(folder.documents.all()), [self.document])

    def test_addition_and_deletion_of_documents(self):
        folder = Folder.objects.create(label=TEST_FOLDER_LABEL)
        folder.documents.add(self.document)

        self.assertEqual(folder.documents.count(), 1)
        self.assertEqual(list(folder.documents.all()), [self.document])

        folder.documents.remove(self.document)

        self.assertEqual(folder.documents.count(), 0)
        self.assertEqual(list(folder.documents.all()), [])
