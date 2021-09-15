from __future__ import absolute_import, unicode_literals

import logging

from django.apps import apps
from django.db import models, transaction
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.models import AccessControlList
from mayan.apps.common.literals import TIME_DELTA_UNIT_CHOICES

from ..events import event_document_type_created, event_document_type_edited
from ..literals import DEFAULT_DELETE_PERIOD, DEFAULT_DELETE_TIME_UNIT
from ..managers import DocumentTypeManager
from ..permissions import permission_document_view
from ..settings import setting_language

__all__ = ('DocumentType', 'DocumentTypeFilename')
logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class DocumentType(models.Model):
    """
    Define document types or classes to which a specific set of
    properties can be attached
    """
    label = models.CharField(
        help_text=_('The name of the document type.'), max_length=96,
        unique=True, verbose_name=_('Label')
    )
    trash_time_period = models.PositiveIntegerField(
        blank=True, help_text=_(
            'Amount of time after which documents of this type will be '
            'moved to the trash.'
        ), null=True, verbose_name=_('Trash time period')
    )
    trash_time_unit = models.CharField(
        blank=True, choices=TIME_DELTA_UNIT_CHOICES, null=True, max_length=8,
        verbose_name=_('Trash time unit')
    )
    delete_time_period = models.PositiveIntegerField(
        blank=True, default=DEFAULT_DELETE_PERIOD, help_text=_(
            'Amount of time after which documents of this type in the trash '
            'will be deleted.'
        ), null=True, verbose_name=_('Delete time period')
    )
    delete_time_unit = models.CharField(
        blank=True, choices=TIME_DELTA_UNIT_CHOICES,
        default=DEFAULT_DELETE_TIME_UNIT, max_length=8, null=True,
        verbose_name=_('Delete time unit')
    )

    objects = DocumentTypeManager()

    class Meta:
        ordering = ('label',)
        verbose_name = _('Document type')
        verbose_name_plural = _('Documents types')

    def __str__(self):
        return self.label

    def delete(self, *args, **kwargs):
        # Delete all documents of this type manually to trigger their
        # .delete() method and storage cleanup routines.
        # https://docs.djangoproject.com/en/1.11/ref/models/querysets/#delete
        Document = apps.get_model(app_label='documents', model_name='Document')
        for document in Document.passthrough.filter(document_type=self):
            document.delete(to_trash=False)

        return super(DocumentType, self).delete(*args, **kwargs)

    @property
    def deleted_documents(self):
        DeletedDocument = apps.get_model(
            app_label='documents', model_name='DeletedDocument'
        )
        return DeletedDocument.objects.filter(document_type=self)

    def get_absolute_url(self):
        return reverse(
            'documents:document_type_document_list', args=(self.pk,)
        )

    def get_document_count(self, user):
        queryset = AccessControlList.objects.filter_by_access(
            permission=permission_document_view, user=user,
            queryset=self.documents
        )
        return queryset.count()
    get_document_count.short_description = _('Documents')

    def natural_key(self):
        return (self.label,)

    def new_document(self, file_object, label=None, description=None, language=None, _user=None):
        try:
            with transaction.atomic():
                document = self.documents.create(
                    description=description or '',
                    label=label or file_object.name,
                    language=language or setting_language.value
                )
                document.save(_user=_user)

                document.new_version(file_object=file_object, _user=_user)
                return document
        except Exception as exception:
            logger.critical(
                'Unexpected exception while trying to create new document '
                '"%s" from document type "%s"; %s',
                label or file_object.name, self, exception
            )
            raise

    def save(self, *args, **kwargs):
        user = kwargs.pop('_user', None)
        created = not self.pk

        result = super(DocumentType, self).save(*args, **kwargs)

        if created:
            event_document_type_created.commit(
                actor=user, target=self
            )
        else:
            event_document_type_edited.commit(
                actor=user, target=self
            )

        return result


@python_2_unicode_compatible
class DocumentTypeFilename(models.Model):
    """
    List of labels available to a specific document type for the
    quick rename functionality
    """
    document_type = models.ForeignKey(
        on_delete=models.CASCADE, related_name='filenames', to=DocumentType,
        verbose_name=_('Document type')
    )
    filename = models.CharField(
        db_index=True, max_length=128, verbose_name=_('Label')
    )
    enabled = models.BooleanField(default=True, verbose_name=_('Enabled'))

    class Meta:
        ordering = ('filename',)
        unique_together = ('document_type', 'filename')
        verbose_name = _('Quick label')
        verbose_name_plural = _('Quick labels')

    def __str__(self):
        return self.filename
