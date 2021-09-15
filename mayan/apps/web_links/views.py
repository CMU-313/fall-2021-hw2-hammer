import logging

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView

from mayan.apps.acls.models import AccessControlList
from mayan.apps.common.generics import (
    AddRemoveView, SingleObjectCreateView, SingleObjectDeleteView,
    SingleObjectEditView, SingleObjectListView
)
from mayan.apps.common.mixins import ExternalObjectMixin
from mayan.apps.documents.events import event_document_type_edited
from mayan.apps.documents.models import Document, DocumentType
from mayan.apps.documents.permissions import permission_document_type_edit

from .events import event_web_link_edited, event_web_link_navigated
from .forms import WebLinkForm
from .icons import icon_web_link_setup
from .links import link_web_link_create
from .models import ResolvedWebLink, WebLink
from .permissions import (
    permission_web_link_create, permission_web_link_delete,
    permission_web_link_edit, permission_web_link_instance_view,
    permission_web_link_view
)

logger = logging.getLogger(name=__name__)


class DocumentTypeWebLinksView(AddRemoveView):
    main_object_method_add = 'web_link_add'
    main_object_method_remove = 'web_link_remove'
    main_object_permission = permission_document_type_edit
    main_object_model = DocumentType
    main_object_pk_url_kwarg = 'document_type_id'
    secondary_object_model = WebLink
    secondary_object_permission = permission_web_link_edit
    list_available_title = _('Available web links')
    list_added_title = _('Web links enabled')
    related_field = 'web_links'

    def action_add(self, queryset, _user):
        with transaction.atomic():
            event_document_type_edited.commit(
                actor=_user, target=self.main_object
            )
            for obj in queryset:
                self.main_object.web_links.add(obj)
                event_web_link_edited.commit(
                    actor=_user, action_object=self.main_object, target=obj
                )

    def action_remove(self, queryset, _user):
        with transaction.atomic():
            event_document_type_edited.commit(
                actor=_user, target=self.main_object
            )
            for obj in queryset:
                self.main_object.web_links.remove(obj)
                event_web_link_edited.commit(
                    actor=_user, action_object=self.main_object, target=obj
                )

    def get_actions_extra_kwargs(self):
        return {'_user': self.request.user}

    def get_extra_context(self):
        return {
            'object': self.main_object,
            'title': _(
                'Web links to enable for document type: %s'
            ) % self.main_object,
        }


class ResolvedWebLinkView(ExternalObjectMixin, RedirectView):
    external_object_class = Document
    external_object_pk_url_kwarg = 'document_id'
    external_object_permission = permission_web_link_instance_view

    def get_redirect_url(self, *args, **kwargs):
        event_web_link_navigated.commit(
            actor=self.request.user, action_object=self.external_object,
            target=self.get_web_link()
        )
        return self.get_web_link().get_url_for(
            document=self.external_object
        )

    def get_web_link(self):
        return get_object_or_404(
            klass=self.get_web_link_queryset(), pk=self.kwargs['web_link_id']
        )

    def get_web_link_queryset(self):
        queryset = ResolvedWebLink.objects.get_for(
            document=self.external_object, user=self.request.user
        )
        return AccessControlList.objects.restrict_queryset(
            permission=permission_web_link_instance_view, queryset=queryset,
            user=self.request.user
        )


class WebLinkDocumentTypesView(AddRemoveView):
    main_object_method_add = 'document_types_add'
    main_object_method_remove = 'document_types_remove'
    main_object_permission = permission_web_link_edit
    main_object_model = WebLink
    main_object_pk_url_kwarg = 'web_link_id'
    secondary_object_model = DocumentType
    secondary_object_permission = permission_document_type_edit
    list_available_title = _('Available document types')
    list_added_title = _('Document types enabled')
    related_field = 'document_types'

    def get_actions_extra_kwargs(self):
        return {'_user': self.request.user}

    def get_extra_context(self):
        return {
            'object': self.main_object,
            'title': _(
                'Document type for which to enable web link: %s'
            ) % self.main_object,
        }


class WebLinkListView(SingleObjectListView):
    model = WebLink
    object_permission = permission_web_link_view

    def get_extra_context(self):
        return {
            'hide_link': True,
            'hide_object': True,
            'no_results_icon': icon_web_link_setup,
            'no_results_main_link': link_web_link_create.resolve(
                context=RequestContext(request=self.request)
            ),
            'no_results_text': _(
                'Web links allow generating HTTP links from documents to '
                'external resources. The link URL\'s can contain document '
                'properties values.'
            ),
            'no_results_title': _(
                'There are no web links'
            ),
            'title': _('Web links'),
        }


class DocumentWebLinkListView(ExternalObjectMixin, WebLinkListView):
    external_object_class = Document
    external_object_permission = permission_web_link_instance_view
    external_object_pk_url_kwarg = 'document_id'
    object_permission = permission_web_link_instance_view

    def get_extra_context(self):
        return {
            'document': self.external_object,
            'hide_link': True,
            'hide_object': True,
            'no_results_icon': icon_web_link_setup,
            'no_results_text': _(
                'Web links allow generating HTTP links from documents to '
                'external resources. The link URL\'s can contain document '
                'properties values.'
            ),
            'no_results_title': _(
                'There are no web links for this document'
            ),
            'object': self.external_object,
            'title': _('Web links for document: %s') % self.external_object,
        }

    def get_web_link_queryset(self):
        return ResolvedWebLink.objects.get_for(
            document=self.external_object, user=self.request.user
        )


class WebLinkCreateView(SingleObjectCreateView):
    extra_context = {'title': _('Create new web link')}
    form_class = WebLinkForm
    post_action_redirect = reverse_lazy(
        viewname='web_links:web_link_list'
    )
    view_permission = permission_web_link_create

    def get_save_extra_data(self):
        return {'_user': self.request.user}


class WebLinkDeleteView(SingleObjectDeleteView):
    model = WebLink
    object_permission = permission_web_link_delete
    pk_url_kwarg = 'web_link_id'
    post_action_redirect = reverse_lazy(
        viewname='web_links:web_link_list'
    )

    def get_extra_context(self):
        return {
            'object': self.object,
            'title': _('Delete web link: %s') % self.object
        }


class WebLinkEditView(SingleObjectEditView):
    form_class = WebLinkForm
    model = WebLink
    object_permission = permission_web_link_edit
    pk_url_kwarg = 'web_link_id'
    post_action_redirect = reverse_lazy(
        viewname='web_links:web_link_list'
    )

    def get_extra_context(self):
        return {
            'object': self.object,
            'title': _('Edit web link: %s') % self.object
        }

    def get_save_extra_data(self):
        return {'_user': self.request.user}
