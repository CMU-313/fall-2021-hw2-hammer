from __future__ import unicode_literals

import logging
import os

from django.db import models

from mayan.apps.django_gpg.exceptions import DecryptionError
from mayan.apps.django_gpg.models import Key
from mayan.apps.documents.models import DocumentVersion
from mayan.apps.storage.utils import mkstemp

logger = logging.getLogger(__name__)


class EmbeddedSignatureManager(models.Manager):
    def open_signed(self, document_version, file_object):
        for signature in self.filter(document_version=document_version):
            try:
                return self.open_signed(
                    file_object=Key.objects.decrypt_file(
                        file_object=file_object
                    ), document_version=document_version
                )
            except DecryptionError:
                file_object.seek(0)
                return file_object
        else:
            return file_object

    def sign_document_version(self, document_version, key, passphrase=None, user=None):
        temporary_file_object, temporary_filename = mkstemp()

        try:
            with document_version.open() as file_object:
                key.sign_file(
                    binary=True, file_object=file_object,
                    output=temporary_filename, passphrase=passphrase
                )
        except Exception:
            raise
        else:
            with open(temporary_filename, mode='rb') as file_object:
                new_version = document_version.document.new_version(
                    file_object=file_object, _user=user
                )
        finally:
            os.unlink(temporary_filename)

        return new_version

    def unsigned_document_versions(self):
        return DocumentVersion.objects.exclude(
            pk__in=self.values('document_version')
        )
