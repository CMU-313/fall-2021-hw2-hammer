from __future__ import unicode_literals

import datetime
import logging
import time

from django.utils.timezone import now

from mayan.apps.common.tests import BaseTestCase
from mayan.apps.documents.tests import DocumentTestMixin
from mayan.apps.documents.tests.literals import TEST_SMALL_DOCUMENT_PATH

from ..exceptions import (
    DocumentAlreadyCheckedOut, DocumentNotCheckedOut,
    NewDocumentVersionNotAllowed
)
from ..models import DocumentCheckout, NewVersionBlock


class DocumentCheckoutTestCase(DocumentTestMixin, BaseTestCase):
    def test_document_checkout(self):
        expiration_datetime = now() + datetime.timedelta(days=1)

        DocumentCheckout.objects.checkout_document(
            document=self.document, expiration_datetime=expiration_datetime,
            user=self._test_case_user, block_new_version=True
        )

        self.assertTrue(self.document.is_checked_out())
        self.assertTrue(
            DocumentCheckout.objects.is_document_checked_out(
                document=self.document
            )
        )

    def test_checkin_in(self):
        expiration_datetime = now() + datetime.timedelta(days=1)

        DocumentCheckout.objects.checkout_document(
            document=self.document, expiration_datetime=expiration_datetime,
            user=self._test_case_user, block_new_version=True
        )

        self.document.check_in()

        self.assertFalse(self.document.is_checked_out())
        self.assertFalse(
            DocumentCheckout.objects.is_document_checked_out(
                document=self.document
            )
        )

    def test_double_checkout(self):
        expiration_datetime = now() + datetime.timedelta(days=1)

        DocumentCheckout.objects.checkout_document(
            document=self.document, expiration_datetime=expiration_datetime,
            user=self._test_case_user, block_new_version=True
        )

        with self.assertRaises(DocumentAlreadyCheckedOut):
            DocumentCheckout.objects.checkout_document(
                document=self.document,
                expiration_datetime=expiration_datetime, user=self._test_case_user,
                block_new_version=True
            )

    def test_checkin_without_checkout(self):
        with self.assertRaises(DocumentNotCheckedOut):
            self.document.check_in()

    def test_auto_checkin(self):
        expiration_datetime = now() + datetime.timedelta(seconds=.1)

        DocumentCheckout.objects.checkout_document(
            document=self.document, expiration_datetime=expiration_datetime,
            user=self._test_case_user, block_new_version=True
        )

        time.sleep(.11)

        DocumentCheckout.objects.check_in_expired_check_outs()

        self.assertFalse(self.document.is_checked_out())


class NewVersionBlockTestCase(DocumentTestMixin, BaseTestCase):
    def test_blocking(self):
        NewVersionBlock.objects.block(document=self.document)

        self.assertEqual(NewVersionBlock.objects.count(), 1)
        self.assertEqual(
            NewVersionBlock.objects.first().document, self.document
        )

    def test_unblocking(self):
        NewVersionBlock.objects.create(document=self.document)

        NewVersionBlock.objects.unblock(document=self.document)

        self.assertEqual(NewVersionBlock.objects.count(), 0)

    def test_is_blocked(self):
        NewVersionBlock.objects.create(document=self.document)

        self.assertTrue(
            NewVersionBlock.objects.is_blocked(document=self.document)
        )

        NewVersionBlock.objects.all().delete()

        self.assertFalse(
            NewVersionBlock.objects.is_blocked(document=self.document)
        )

    def test_blocking_new_versions(self):
        # Silence unrelated logging
        logging.getLogger('mayan.apps.documents.models').setLevel(
            level=logging.CRITICAL
        )

        NewVersionBlock.objects.block(document=self.document)

        with self.assertRaises(NewDocumentVersionNotAllowed):
            with open(TEST_SMALL_DOCUMENT_PATH, mode='rb') as file_object:
                self.document.new_version(file_object=file_object)

    def test_version_creation_blocking(self):
        expiration_datetime = now() + datetime.timedelta(days=1)

        # Silence unrelated logging
        logging.getLogger('mayan.apps.documents.models').setLevel(
            level=logging.CRITICAL
        )

        DocumentCheckout.objects.checkout_document(
            document=self.document, expiration_datetime=expiration_datetime,
            user=self._test_case_user, block_new_version=True
        )

        with self.assertRaises(NewDocumentVersionNotAllowed):
            with open(TEST_SMALL_DOCUMENT_PATH, mode='rb') as file_object:
                self.document.new_version(file_object=file_object)
