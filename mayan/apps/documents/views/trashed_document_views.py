import logging

from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _, ungettext

from mayan.apps.acls.models import AccessControlList
from mayan.apps.common.settings import setting_home_view
from mayan.apps.views.generics import (
    ConfirmView, MultipleObjectConfirmActionView
)

from ..icons import icon_document_list_deleted
from ..models.document_models import Document
from ..models.trashed_document_models import TrashedDocument
from ..permissions import (
    permission_trashed_document_delete, permission_trashed_document_restore,
    permission_document_trash, permission_document_view,
    permission_trash_empty
)
from ..tasks import task_trashed_document_delete, task_trash_can_empty

from .document_views import DocumentListView

__all__ = (
    'DocumentTrashView', 'EmptyTrashCanView', 'TrashedDocumentDeleteView',
    'TrashedDocumentListView', 'TrashedDocumentRestoreView'
)
logger = logging.getLogger(name=__name__)


class DocumentTrashView(MultipleObjectConfirmActionView):
    object_permission = permission_document_trash
    pk_url_kwarg = 'document_id'
    source_queryset = Document.valid
    success_message_singular = _(
        '%(count)d document moved to the trash.'
    )
    success_message_plural = _(
        '%(count)d documents moved to the trash.'
    )

    def get_extra_context(self):
        context = {
            'title': ungettext(
                singular='Move the selected document to the trash?',
                plural='Move the selected documents to the trash?',
                number=self.object_list.count()
            )
        }

        if self.object_list.count() == 1:
            context['object'] = self.object_list.first()

        return context

    def get_post_action_redirect(self):
        # Return to the previous view after moving the document to trash
        # unless the move happened from the document view, in which case
        # redirecting back to the document is not possible because it is
        # now a trashed document and not accessible.
        if 'document_id' in self.kwargs:
            return reverse(viewname=setting_home_view.value)
        else:
            return None

    def object_action(self, form, instance):
        instance.delete(_user=self.request.user)


class EmptyTrashCanView(ConfirmView):
    action_cancel_redirect = post_action_redirect = reverse_lazy(
        'documents:document_list_deleted'
    )
    extra_context = {
        'title': _('Empty trash?')
    }
    view_permission = permission_trash_empty

    def view_action(self):
        task_trash_can_empty.apply_async()

        messages.success(
            message=_('The trash emptying task has been queued.'),
            request=self.request
        )


class TrashedDocumentDeleteView(MultipleObjectConfirmActionView):
    model = TrashedDocument
    object_permission = permission_trashed_document_delete
    pk_url_kwarg = 'document_id'
    success_message_singular = _(
        '%(count)d trashed document submitted for deletion.'
    )
    success_message_plural = _(
        '%(count)d trashed documents submitted for deletion.'
    )

    def get_extra_context(self):
        context = {
            'title': ungettext(
                singular='Delete the selected trashed document?',
                plural='Delete the selected trashed documents?',
                number=self.object_list.count()
            )
        }

        if self.object_list.count() == 1:
            context['object'] = self.object_list.first()

        return context

    def object_action(self, form, instance):
        task_trashed_document_delete.apply_async(
            kwargs={'trashed_document_id': instance.pk}
        )


class TrashedDocumentListView(DocumentListView):
    object_permission = None

    def get_document_queryset(self):
        return AccessControlList.objects.restrict_queryset(
            permission=permission_document_view,
            queryset=TrashedDocument.trash.all(),
            user=self.request.user
        )

    def get_extra_context(self):
        context = super().get_extra_context()
        context.update(
            {
                'hide_link': True,
                'no_results_icon': icon_document_list_deleted,
                'no_results_text': _(
                    'To avoid loss of data, documents are not deleted '
                    'instantly. First, they are placed in the trash can. '
                    'From here they can be then finally deleted or restored.'
                ),
                'no_results_title': _(
                    'There are no documents in the trash can'
                ),
                'title': _('Documents in trash'),
            }
        )
        return context


class TrashedDocumentRestoreView(MultipleObjectConfirmActionView):
    model = TrashedDocument
    object_permission = permission_trashed_document_restore
    pk_url_kwarg = 'document_id'
    success_message_singular = _(
        '%(count)d trashed document restored.'
    )
    success_message_plural = _(
        '%(count)d trashed documents restored.'
    )

    def get_extra_context(self):
        context = {
            'title': ungettext(
                singular='Restore the selected trashed document?',
                plural='Restore the selected trashed documents?',
                number=self.object_list.count()
            )
        }

        if self.object_list.count() == 1:
            context['object'] = self.object_list.first()

        return context

    def object_action(self, form, instance):
        instance.restore()
