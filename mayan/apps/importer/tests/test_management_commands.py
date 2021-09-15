from __future__ import unicode_literals

import csv

from django.core import management
from django.utils.encoding import force_bytes, force_text

from mayan.apps.documents.models import DocumentType, Document
from mayan.apps.documents.tests.base import GenericDocumentTestCase
from mayan.apps.documents.tests.literals import TEST_SMALL_DOCUMENT_PATH
from mayan.apps.storage.utils import fs_cleanup, mkstemp


class ImportManagementCommandTestCase(GenericDocumentTestCase):
    auto_generate_test_csv_file = True
    auto_upload_document = False
    random_primary_key_enable = False
    test_import_count = 1

    def setUp(self):
        super(ImportManagementCommandTestCase, self).setUp()
        if self.auto_generate_test_csv_file:
            self._create_test_csv_file()

    def tearDown(self):
        self._destroy_test_csv_file()
        super(ImportManagementCommandTestCase, self).tearDown()

    def _create_test_csv_file(self):
        self.test_csv_path = mkstemp()[1]

        print('Test CSV file: {}'.format(self.test_csv_path))

        with open(self.test_csv_path, mode='w', newline='') as file_object:
            filewriter = csv.writer(
                file_object, delimiter=',', quotechar='"',
                quoting=csv.QUOTE_MINIMAL
            )
            print(
                'Generating test CSV for {} documents'.format(
                    self.test_import_count
                )
            )
            for times in range(self.test_import_count):
                filewriter.writerow(
                    [
                        self.test_document_type.label, TEST_SMALL_DOCUMENT_PATH,
                        'column 2', 'column 3', 'column 4', 'column 5',
                        'part #', 'value',
                    ]
                )
                filewriter.writerow(
                    [
                        self.test_document_type.label, TEST_SMALL_DOCUMENT_PATH,
                        'column 2', 'column 3', 'column 4', 'column 5',
                        'part#', 'value',
                    ]
                )

    def _destroy_test_csv_file(self):
        fs_cleanup(filename=self.test_csv_path)

    def test_import_csv_read(self):
        self.test_document_type.delete()
        management.call_command('import', self.test_csv_path)

        self.assertTrue(DocumentType.objects.count() > 0)
        self.assertTrue(Document.objects.count() > 0)

    def test_import_document_type_column_mapping(self):
        self.test_document_type.delete()
        management.call_command(
            'import', self.test_csv_path, '--document_type_column', '2'
        )

        self.assertTrue(DocumentType.objects.first().label == 'column 2')
        self.assertTrue(Document.objects.count() > 0)

    def test_import_document_path_column_mapping(self):
        self.test_document_type.delete()
        with self.assertRaises(IOError):
            management.call_command(
                'import', self.test_csv_path, '--document_path_column', '2'
            )

    def test_import_metadata_column_mapping(self):
        self.test_document_type.delete()
        management.call_command(
            'import', self.test_csv_path, '--metadata_pairs_column', '2:3,4:5',
        )

        self.assertTrue(DocumentType.objects.count() > 0)
        self.assertTrue(Document.objects.count() > 0)
        self.assertTrue(Document.objects.first().metadata.count() > 0)
        self.assertEqual(
            Document.objects.first().metadata.get(
                metadata_type__name='column_2'
            ).value, 'column 3'
        )

    def test_import_ambiguous_metadata(self):
        self.auto_generate_test_csv_file = False
        self.test_import_count = 2

        self.test_document_type.delete()
        management.call_command(
            'import', self.test_csv_path, '--metadata_pairs_column', '6:7',
        )

        self.assertTrue(DocumentType.objects.count() > 0)
        self.assertTrue(Document.objects.count() > 0)
        self.assertTrue(Document.objects.first().metadata.count() > 0)
        self.assertEqual(
            Document.objects.first().metadata.get(
                metadata_type__name='part'
            ).value, 'value'
        )
