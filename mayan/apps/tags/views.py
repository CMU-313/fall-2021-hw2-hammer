from __future__ import absolute_import, unicode_literals

import logging

from django.contrib import messages
from django.shortcuts import reverse
from django.template import RequestContext
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _, ungettext

from mayan.apps.acls.models import AccessControlList
from mayan.apps.common.generics import (
    MultipleObjectFormActionView, MultipleObjectConfirmActionView,
    SingleObjectCreateView, SingleObjectEditView, SingleObjectListView
)
from mayan.apps.common.mixins import ExternalObjectMixin
from mayan.apps.documents.models import Document
from mayan.apps.documents.views import DocumentListView

from .forms import TagMultipleSelectionForm
from .icons import (
    icon_document_tag_multiple_attach, icon_document_tag_multiple_remove,
    icon_menu_tags, icon_tag_delete_submit
)
from .links import link_document_tag_multiple_attach, link_tag_create
from .models import Tag
from .permissions import (
    permission_tag_attach, permission_tag_create, permission_tag_delete,
    permission_tag_edit, permission_tag_remove, permission_tag_view
)

logger = logging.getLogger(__name__)


class TagAttachActionView(MultipleObjectFormActionView):
    form_class = TagMultipleSelectionForm
    model = Document
    pk_url_kwarg = 'document_id'
    object_permission = permission_tag_attach
    success_message_single = _(
        'Tag attach request performed on %(object)s.'
    )
    success_message_singular = _(
        'Tag attach request performed on %(count)d document.'
    )
    success_message_plural = _(
        'Tag attach request performed on %(count)d documents.'
    )
    title_single = 'Attach tags to: %(object)s.'
    title_singular = 'Attach tags to %(count)d document.'
    title_plural = 'Attach tags to %(count)d documents.'

    def get_extra_context(self):
        return {
            'submit_icon_class': icon_document_tag_multiple_attach,
            'submit_label': _('Attach'),
        }

    def get_form_extra_kwargs(self):
        queryset = self.get_object_list()
        result = {
            'help_text': _('Tags to be attached.'),
            'permission': permission_tag_attach,
            'user': self.request.user
        }

        if queryset.count() == 1:
            result.update(
                {
                    'queryset': Tag.objects.exclude(
                        pk__in=queryset.first().tags.all()
                    )
                }
            )

        return result

    def get_post_action_redirect(self):
        queryset = self.get_object_list()
        if queryset.count() == 1:
            return reverse(
                viewname='tags:document_tag_list', kwargs={
                    'document_id': queryset.first().pk
                }
            )
        else:
            return super(TagAttachActionView, self).get_post_action_redirect()

    def object_action(self, form, instance):
        attached_tags = instance.get_tags(
            permission=permission_tag_attach, user=self.request.user
        )

        tag_list = AccessControlList.objects.restrict_queryset(
            permission=permission_tag_attach, queryset=form.cleaned_data['tags'],
            user=self.request.user
        )

        for tag in tag_list:
            if tag in attached_tags:
                messages.warning(
                    message=_(
                        'Document "%(document)s" is already tagged as '
                        '"%(tag)s"'
                    ) % {
                        'document': instance, 'tag': tag
                    }, request=self.request
                )
            else:
                queryset = Document.objects.filter(pk=instance.pk)
                tag.documents_attach(queryset=queryset, _user=self.request.user)
                messages.success(
                    message=_(
                        'Tag "%(tag)s" attached successfully to document '
                        '"%(document)s".'
                    ) % {
                        'document': instance, 'tag': tag
                    }, request=self.request
                )


class TagCreateView(SingleObjectCreateView):
    extra_context = {'title': _('Create tag')}
    fields = ('label', 'color')
    model = Tag
    post_action_redirect = reverse_lazy(viewname='tags:tag_list')
    view_permission = permission_tag_create

    def get_save_extra_data(self):
        return {'_user': self.request.user}


class TagDeleteActionView(MultipleObjectConfirmActionView):
    model = Tag
    pk_url_kwarg = 'tag_id'
    post_action_redirect = reverse_lazy(viewname='tags:tag_list')
    object_permission = permission_tag_delete
    success_message_singular = _('Tag delete request performed on %(count)d tag')
    success_message_plural = _(
        'Tag delete request performed on %(count)d tags'
    )

    def get_extra_context(self):
        queryset = self.get_queryset()

        result = {
            'message': _('Will be removed from all documents.'),
            'submit_icon_class': icon_tag_delete_submit,
            'submit_label': _('Delete'),
            'title': ungettext(
                singular='Delete the selected tag?',
                plural='Delete the selected tags?',
                number=queryset.count()
            )
        }

        if queryset.count() == 1:
            result.update(
                {
                    'object': queryset.first(),
                    'title': _('Delete tag: %s') % queryset.first()
                }
            )

        return result

    def object_action(self, instance, form=None):
        try:
            instance.delete()
            messages.success(
                message=_('Tag "%s" deleted successfully.') % instance,
                request=self.request
            )
        except Exception as exception:
            messages.error(
                message=_('Error deleting tag "%(tag)s": %(error)s') % {
                    'tag': instance, 'error': exception
                }, request=self.request
            )


class TagEditView(SingleObjectEditView):
    fields = ('label', 'color')
    model = Tag
    object_permission = permission_tag_edit
    pk_url_kwarg = 'tag_id'
    post_action_redirect = reverse_lazy(viewname='tags:tag_list')

    def get_extra_context(self):
        return {
            'object': self.get_object(),
            'title': _('Edit tag: %s') % self.get_object(),
        }

    def get_save_extra_data(self):
        return {'_user': self.request.user}


class TagListView(SingleObjectListView):
    object_permission = permission_tag_view

    def get_extra_context(self):
        return {
            'hide_link': True,
            'hide_object': True,
            'no_results_icon': icon_menu_tags,
            'no_results_main_link': link_tag_create.resolve(
                context=RequestContext(request=self.request)
            ),
            'no_results_text': _(
                'Tags are color coded properties that can be attached or '
                'removed from documents.'
            ),
            'no_results_title': _('No tags available'),
            'title': _('Tags'),
        }

    def get_source_queryset(self):
        return Tag.objects.all()


class TagDocumentListView(ExternalObjectMixin, DocumentListView):
    external_object_class = Tag
    external_object_permission = permission_tag_view
    external_object_pk_url_kwarg = 'tag_id'

    def get_document_queryset(self):
        return self.get_tag().get_documents(user=self.request.user).all()

    def get_extra_context(self):
        context = super(TagDocumentListView, self).get_extra_context()
        context.update(
            {
                'column_class': 'col-xs-12 col-sm-6 col-md-4 col-lg-3',
                'object': self.get_tag(),
                'title': _('Documents with the tag: %s') % self.get_tag(),
            }
        )
        return context

    def get_tag(self):
        return self.get_external_object()


class DocumentTagListView(ExternalObjectMixin, TagListView):
    external_object_class = Document
    external_object_permission = permission_tag_view
    external_object_pk_url_kwarg = 'document_id'

    def get_extra_context(self):
        context = super(DocumentTagListView, self).get_extra_context()
        context.update(
            {
                'hide_link': True,
                'no_results_main_link': link_document_tag_multiple_attach.resolve(
                    context=RequestContext(
                        self.request, {'object': self.get_external_object()}
                    )
                ),
                'no_results_title': _('Document has no tags attached'),
                'object': self.get_external_object(),
                'title': _(
                    'Tags for document: %s'
                ) % self.get_external_object(),
            }
        )
        return context

    def get_source_queryset(self):
        return self.get_external_object().get_tags(
            permission=permission_tag_view, user=self.request.user
        ).all()


class TagRemoveActionView(MultipleObjectFormActionView):
    form_class = TagMultipleSelectionForm
    model = Document
    object_permission = permission_tag_remove
    pk_url_kwarg = 'document_id'
    success_message_single = _(
        'Tag remove request performed on %(object)s.'
    )
    success_message_singular = _(
        'Tag remove request performed on %(count)d document'
    )
    success_message_plural = _(
        'Tag remove request performed on %(count)d documents'
    )
    title_single = 'Remove tags from: %(object)s.'
    title_singular = 'Remove tags from %(count)d document.'
    title_plural = 'Remove tags from %(count)d documents.'

    def get_extra_context(self):
        return {
            'submit_icon_class': icon_document_tag_multiple_remove,
            'submit_label': _('Remove'),
        }

    def get_form_extra_kwargs(self):
        queryset = self.get_object_list()
        result = {
            'help_text': _('Tags to be removed.'),
            'permission': permission_tag_remove,
            'user': self.request.user
        }

        if queryset.count() == 1:
            result.update(
                {
                    'queryset': queryset.first().tags.all()
                }
            )

        return result

    def get_post_action_redirect(self):
        queryset = self.get_object_list()
        if queryset.count() == 1:
            return reverse(
                viewname='tags:document_tag_list', kwargs={
                    'document_id': queryset.first().pk
                }
            )
        else:
            return super(TagRemoveActionView, self).get_post_action_redirect()

    def object_action(self, form, instance):
        attached_tags = instance.get_tags(
            permission=permission_tag_remove, user=self.request.user
        )

        tag_list = AccessControlList.objects.restrict_queryset(
            permission=permission_tag_remove,
            queryset=form.cleaned_data['tags'],
            user=self.request.user
        )

        for tag in tag_list:
            if tag not in attached_tags:
                messages.warning(
                    message=_(
                        'Document "%(document)s" wasn\'t tagged as "%(tag)s'
                    ) % {
                        'document': instance, 'tag': tag
                    }, request=self.request
                )
            else:
                queryset = Document.objects.filter(pk=instance.pk)
                tag.documents_remove(queryset=queryset, _user=self.request.user)
                messages.success(
                    message=_(
                        'Tag "%(tag)s" removed successfully from document '
                        '"%(document)s".'
                    ) % {
                        'document': instance, 'tag': tag
                    }, request=self.request
                )
