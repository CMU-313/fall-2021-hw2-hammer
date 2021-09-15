from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from mayan.apps.documents.models import (
    DocumentType, DocumentVersion, DocumentVersionPage
)

from .managers import (
    DocumentVersionPageContentManager, DocumentTypeSettingsManager
)


class DocumentTypeSettings(models.Model):
    """
    This model stores the parsing settings for a document type.
    """
    document_type = models.OneToOneField(
        on_delete=models.CASCADE, related_name='parsing_settings',
        to=DocumentType, unique=True, verbose_name=_('Document type')
    )
    auto_parsing = models.BooleanField(
        default=True, verbose_name=_(
            'Automatically queue newly created documents for parsing.'
        )
    )

    objects = DocumentTypeSettingsManager()

    def natural_key(self):
        return self.document_type.natural_key()
    natural_key.dependencies = ['documents.DocumentType']

    class Meta:
        verbose_name = _('Document type settings')
        verbose_name_plural = _('Document types settings')


@python_2_unicode_compatible
class DocumentVersionPageContent(models.Model):
    """
    This model store's the parsed content of a document page.
    """
    document_version_page = models.OneToOneField(
        on_delete=models.CASCADE, related_name='content',
        to=DocumentVersionPage, verbose_name=_('Document version page')
    )
    content = models.TextField(
        blank=True, help_text=_(
            'The actual text content as extracted by the document '
            'parsing backend.'
        ), verbose_name=_('Content')
    )

    objects = DocumentVersionPageContentManager()

    class Meta:
        verbose_name = _('Document version page content')
        verbose_name_plural = _('Document version pages contents')

    def __str__(self):
        return force_text(self.document_page)


@python_2_unicode_compatible
class DocumentVersionParseError(models.Model):
    """
    This module stores the errors captures when attempting to parse a
    document version.
    """
    document_version = models.ForeignKey(
        on_delete=models.CASCADE, related_name='parsing_errors',
        to=DocumentVersion, verbose_name=_('Document version')
    )
    datetime_submitted = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name=_('Date time submitted')
    )
    result = models.TextField(blank=True, null=True, verbose_name=_('Result'))

    class Meta:
        ordering = ('datetime_submitted',)
        verbose_name = _('Document version parse error')
        verbose_name_plural = _('Document version parse errors')

    def __str__(self):
        return force_text(self.document_version)
