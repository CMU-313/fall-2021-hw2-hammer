from __future__ import absolute_import, unicode_literals

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.models import AccessControlList
from mayan.apps.common.generics import (
    ConfirmView, SingleObjectCreateView, SingleObjectDetailView
)
from mayan.apps.common.utils import encapsulate
from mayan.apps.documents.models import Document
from mayan.apps.documents.views import DocumentListView

from .exceptions import DocumentAlreadyCheckedOut, DocumentNotCheckedOut
from .forms import DocumentCheckoutDefailForm, DocumentCheckoutForm
from .icons import icon_checkout_info
from .models import DocumentCheckout
from .permissions import (
    permission_document_checkin, permission_document_checkin_override,
    permission_document_checkout, permission_document_checkout_detail_view
)


class CheckoutDocumentView(SingleObjectCreateView):
    form_class = DocumentCheckoutForm

    def dispatch(self, request, *args, **kwargs):
        self.document = get_object_or_404(klass=Document, pk=self.kwargs['pk'])

        AccessControlList.objects.check_access(
            permissions=permission_document_checkout, user=request.user,
            obj=self.document
        )

        return super(
            CheckoutDocumentView, self
        ).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            instance = form.save(commit=False)
            instance.user = self.request.user
            instance.document = self.document
            instance.save()
        except DocumentAlreadyCheckedOut:
            messages.error(self.request, _('Document already checked out.'))
        except Exception as exception:
            messages.error(
                self.request,
                _('Error trying to check out document; %s') % exception
            )
        else:
            messages.success(
                self.request,
                _('Document "%s" checked out successfully.') % self.document
            )

        return HttpResponseRedirect(self.get_success_url())

    def get_extra_context(self):
        return {
            'object': self.document,
            'title': _('Check out document: %s') % self.document
        }

    def get_post_action_redirect(self):
        return reverse('checkouts:checkout_info', args=(self.document.pk,))


class CheckoutListView(DocumentListView):
    def get_document_queryset(self):
        return AccessControlList.objects.filter_by_access(
            permission=permission_document_checkout_detail_view,
            user=self.request.user,
            queryset=DocumentCheckout.objects.checked_out_documents()
        )

    def get_extra_context(self):
        context = super(CheckoutListView, self).get_extra_context()
        context.update(
            {
                'extra_columns': (
                    {
                        'name': _('User'),
                        'attribute': encapsulate(
                            lambda document: document.get_checkout_info().user.get_full_name() or document.get_checkout_info().user
                        )
                    },
                    {
                        'name': _('Checkout time and date'),
                        'attribute': encapsulate(
                            lambda document: document.get_checkout_info().checkout_datetime
                        )
                    },
                    {
                        'name': _('Checkout expiration'),
                        'attribute': encapsulate(
                            lambda document: document.get_checkout_info().expiration_datetime
                        )
                    },
                ),
                'no_results_icon': icon_checkout_info,
                'no_results_text': _(
                    'Checking out a document blocks certain document '
                    'operations for a predetermined amount of '
                    'time.'
                ),
                'no_results_title': _('No documents have been checked out'),
                'title': _('Documents checked out'),
            }
        )
        return context


class CheckoutDetailView(SingleObjectDetailView):
    form_class = DocumentCheckoutDefailForm
    model = Document
    object_permission = permission_document_checkout_detail_view

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _(
                'Check out details for document: %s'
            ) % self.get_object()
        }

    def get_object(self):
        return get_object_or_404(klass=Document, pk=self.kwargs['pk'])


class DocumentCheckinView(ConfirmView):
    def get_extra_context(self):
        document = self.get_object()

        context = {
            'object': document,
        }

        if document.get_checkout_info().user != self.request.user:
            context['title'] = _(
                'You didn\'t originally checked out this document. '
                'Forcefully check in the document: %s?'
            ) % document
        else:
            context['title'] = _('Check in the document: %s?') % document

        return context

    def get_object(self):
        return get_object_or_404(klass=Document, pk=self.kwargs['pk'])

    def get_post_action_redirect(self):
        return reverse('checkouts:checkout_info', args=(self.get_object().pk,))

    def view_action(self):
        document = self.get_object()

        if document.get_checkout_info().user == self.request.user:
            AccessControlList.objects.check_access(
                permissions=permission_document_checkin,
                user=self.request.user, obj=document
            )
        else:
            AccessControlList.objects.check_access(
                permissions=permission_document_checkin_override,
                user=self.request.user, obj=document
            )

        try:
            document.check_in(user=self.request.user)
        except DocumentNotCheckedOut:
            messages.error(
                self.request, _('Document has not been checked out.')
            )
        except Exception as exception:
            messages.error(
                self.request,
                _('Error trying to check in document; %s') % exception
            )
        else:
            messages.success(
                self.request,
                _('Document "%s" checked in successfully.') % document
            )
