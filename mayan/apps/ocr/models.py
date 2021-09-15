from django.db import models
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from mayan.apps.documents.models.document_type_models import DocumentType
from mayan.apps.documents.models.document_version_models import DocumentVersion
from mayan.apps.documents.models.document_version_page_models import DocumentVersionPage

from .managers import (
    DocumentVersionPageOCRContentManager, DocumentTypeSettingsManager
)


class DocumentTypeOCRSettings(models.Model):
    """
    Model to store the OCR settings for a document type.
    """
    document_type = models.OneToOneField(
        on_delete=models.CASCADE, related_name='ocr_settings',
        to=DocumentType, unique=True, verbose_name=_('Document type')
    )
    auto_ocr = models.BooleanField(
        default=True,
        verbose_name=_('Automatically queue newly created documents for OCR.')
    )

    objects = DocumentTypeSettingsManager()

    class Meta:
        verbose_name = _('Document type settings')
        verbose_name_plural = _('Document types settings')

    def natural_key(self):
        return self.document_type.natural_key()
    natural_key.dependencies = ['documents.DocumentType']


class DocumentVersionOCRError(models.Model):
    """
    This models keeps track of the errors captured during the OCR of a
    document version page images.
    """
    document_version = models.ForeignKey(
        on_delete=models.CASCADE, related_name='ocr_errors',
        to=DocumentVersion, verbose_name=_('Document version')
    )
    datetime_submitted = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name=_('Date time submitted')
    )
    result = models.TextField(blank=True, null=True, verbose_name=_('Result'))

    class Meta:
        ordering = ('datetime_submitted',)
        verbose_name = _('Document version OCR error')
        verbose_name_plural = _('Document version OCR errors')

    def __str__(self):
        return force_text(s=self.document_version)


class DocumentVersionPageOCRContent(models.Model):
    """
    This model stores the OCR results for a document version page.
    """
    document_version_page = models.OneToOneField(
        on_delete=models.CASCADE, related_name='ocr_content',
        to=DocumentVersionPage, verbose_name=_('Document version page')
    )
    content = models.TextField(
        blank=True, help_text=_(
            'The actual text content extracted by the OCR backend.'
        ), verbose_name=_('Content')
    )

    objects = DocumentVersionPageOCRContentManager()

    class Meta:
        verbose_name = _('Document version page OCR content')
        verbose_name_plural = _('Document version pages OCR contents')

    def __str__(self):
        return force_text(s=self.document_version_page)
