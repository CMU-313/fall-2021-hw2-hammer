from __future__ import absolute_import, unicode_literals

import logging

from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.models import AccessControlList
from mayan.apps.common.generics import (
    SingleObjectCreateView, SingleObjectDeleteView, SingleObjectEditView,
    SingleObjectListView
)

from ..forms import DocumentTypeFilenameForm_create
from ..icons import icon_document_type_filename, icon_document_type_setup
from ..links import (
    link_document_type_create, link_document_type_filename_create
)
from ..models import DocumentType, DocumentTypeFilename
from ..permissions import (
    permission_document_type_create, permission_document_type_delete,
    permission_document_type_edit, permission_document_type_view
)

from .document_views import DocumentListView

__all__ = (
    'DocumentTypeCreateView', 'DocumentTypeDeleteView',
    'DocumentTypeDocumentListView', 'DocumentTypeEditView',
    'DocumentTypeListView', 'DocumentTypeFilenameCreateView',
    'DocumentTypeFilenameDeleteView', 'DocumentTypeFilenameEditView',
    'DocumentTypeFilenameListView'
)
logger = logging.getLogger(__name__)


class DocumentTypeCreateView(SingleObjectCreateView):
    fields = (
        'label', 'trash_time_period', 'trash_time_unit', 'delete_time_period',
        'delete_time_unit'
    )
    model = DocumentType
    post_action_redirect = reverse_lazy('documents:document_type_list')
    view_permission = permission_document_type_create

    def get_extra_context(self):
        return {
            'title': _('Create document type'),
        }

    def get_save_extra_data(self):
        return {
            '_user': self.request.user,
        }


class DocumentTypeDeleteView(SingleObjectDeleteView):
    model = DocumentType
    object_permission = permission_document_type_delete
    post_action_redirect = reverse_lazy('documents:document_type_list')

    def get_extra_context(self):
        return {
            'message': _('All documents of this type will be deleted too.'),
            'object': self.get_object(),
            'title': _('Delete the document type: %s?') % self.get_object(),
        }


class DocumentTypeDocumentListView(DocumentListView):
    def get_document_type(self):
        return get_object_or_404(klass=DocumentType, pk=self.kwargs['pk'])

    def get_document_queryset(self):
        return self.get_document_type().documents.all()

    def get_extra_context(self):
        context = super(DocumentTypeDocumentListView, self).get_extra_context()
        context.update(
            {
                'object': self.get_document_type(),
                'title': _('Documents of type: %s') % self.get_document_type()
            }
        )
        return context


class DocumentTypeEditView(SingleObjectEditView):
    fields = (
        'label', 'trash_time_period', 'trash_time_unit', 'delete_time_period',
        'delete_time_unit'
    )
    model = DocumentType
    object_permission = permission_document_type_edit
    post_action_redirect = reverse_lazy('documents:document_type_list')

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Edit document type: %s') % self.get_object(),
        }

    def get_save_extra_data(self):
        return {
            '_user': self.request.user,
        }


class DocumentTypeListView(SingleObjectListView):
    model = DocumentType
    object_permission = permission_document_type_view

    def get_extra_context(self):
        return {
            'hide_link': True,
            'hide_object': True,
            'no_results_icon': icon_document_type_setup,
            'no_results_main_link': link_document_type_create.resolve(
                context=RequestContext(request=self.request)
            ),
            'no_results_text': _(
                'Document types are the most basic units of configuration. '
                'Everything in the system will depend on them. '
                'Define a document type for each type of physical '
                'document you intend to upload. Example document types: '
                'invoice, receipt, manual, prescription, balance sheet.'
            ),
            'no_results_title': _('No document types available'),
            'title': _('Document types'),
        }


class DocumentTypeFilenameCreateView(SingleObjectCreateView):
    form_class = DocumentTypeFilenameForm_create

    def dispatch(self, request, *args, **kwargs):
        AccessControlList.objects.check_access(
            permissions=permission_document_type_edit, user=request.user,
            obj=self.get_document_type()
        )

        return super(DocumentTypeFilenameCreateView, self).dispatch(
            request, *args, **kwargs
        )

    def get_document_type(self):
        return get_object_or_404(klass=DocumentType, pk=self.kwargs['pk'])

    def get_extra_context(self):
        return {
            'document_type': self.get_document_type(),
            'navigation_object_list': ('document_type',),
            'title': _(
                'Create quick label for document type: %s'
            ) % self.get_document_type(),
        }

    def get_instance_extra_data(self):
        return {'document_type': self.get_document_type()}


class DocumentTypeFilenameDeleteView(SingleObjectDeleteView):
    model = DocumentTypeFilename
    object_permission = permission_document_type_edit

    def get_extra_context(self):
        return {
            'document_type': self.get_object().document_type,
            'filename': self.get_object(),
            'navigation_object_list': ('document_type', 'filename',),
            'title': _(
                'Delete the quick label: %(label)s, from document type '
                '"%(document_type)s"?'
            ) % {
                'document_type': self.get_object().document_type,
                'label': self.get_object()
            },
        }

    def get_post_action_redirect(self):
        return reverse(
            'documents:document_type_filename_list',
            args=(self.get_object().document_type.pk,)
        )


class DocumentTypeFilenameEditView(SingleObjectEditView):
    fields = ('enabled', 'filename',)
    model = DocumentTypeFilename
    object_permission = permission_document_type_edit

    def get_extra_context(self):
        document_type_filename = self.get_object()

        return {
            'document_type': document_type_filename.document_type,
            'filename': document_type_filename,
            'navigation_object_list': ('document_type', 'filename',),
            'title': _(
                'Edit quick label "%(filename)s" from document type '
                '"%(document_type)s"'
            ) % {
                'document_type': document_type_filename.document_type,
                'filename': document_type_filename
            },
        }

    def get_post_action_redirect(self):
        return reverse(
            'documents:document_type_filename_list',
            args=(self.get_object().document_type.pk,)
        )


class DocumentTypeFilenameListView(SingleObjectListView):
    access_object_retrieve_method = 'get_document_type'
    object_permission = permission_document_type_view

    def get_document_type(self):
        return get_object_or_404(klass=DocumentType, pk=self.kwargs['pk'])

    def get_extra_context(self):
        return {
            'document_type': self.get_document_type(),
            'hide_link': True,
            'hide_object': True,
            'navigation_object_list': ('document_type',),
            'no_results_icon': icon_document_type_filename,
            'no_results_main_link': link_document_type_filename_create.resolve(
                context=RequestContext(
                    request=self.request, dict_={
                        'document_type': self.get_document_type()
                    }
                )
            ),
            'no_results_text': _(
                'Quick labels are predetermined filenames that allow '
                'the quick renaming of documents as they are uploaded '
                'by selecting them from a list. Quick labels can also '
                'be used after the documents have been uploaded.'
            ),
            'no_results_title': _(
                'There are no quick labels for this document type'
            ),
            'title': _(
                'Quick labels for document type: %s'
            ) % self.get_document_type(),
        }

    def get_object_list(self):
        return self.get_document_type().filenames.all()
