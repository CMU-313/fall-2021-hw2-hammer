from __future__ import absolute_import, unicode_literals

from django.apps import apps
from django.db.models.signals import m2m_changed, pre_delete
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls import ModelPermission
from mayan.apps.acls.links import link_acl_list
from mayan.apps.acls.permissions import permission_acl_edit, permission_acl_view
from mayan.apps.common import (
    MayanAppConfig, menu_facet, menu_list_facet, menu_object, menu_main,
    menu_multi_item, menu_sidebar
)
from mayan.apps.common.classes import ModelAttribute, ModelField
from mayan.apps.documents.search import document_page_search, document_search
from mayan.apps.events import ModelEventType
from mayan.apps.events.links import (
    link_events_for_object, link_object_event_types_user_subcriptions_list,
)
from mayan.apps.events.permissions import permission_events_view
from mayan.apps.navigation import SourceColumn

from .events import (
    event_tag_attach, event_tag_created, event_tag_edited, event_tag_remove
)
from .handlers import handler_index_document, handler_tag_pre_delete
from .links import (
    link_document_tag_list, link_multiple_documents_attach_tag,
    link_multiple_documents_tag_remove,
    link_single_document_multiple_tag_remove, link_tag_attach,
    link_tag_create, link_tag_delete, link_tag_edit, link_tag_list,
    link_tag_multiple_delete, link_tag_tagged_item_list
)
from .menus import menu_tags
from .methods import method_get_tags
from .permissions import (
    permission_tag_attach, permission_tag_delete, permission_tag_edit,
    permission_tag_remove, permission_tag_view
)
from .search import tag_search  # NOQA
from .widgets import widget_document_tags


class TagsApp(MayanAppConfig):
    app_namespace = 'tags'
    app_url = 'tags'
    has_rest_api = True
    has_tests = True
    name = 'mayan.apps.tags'
    verbose_name = _('Tags')

    def ready(self):
        super(TagsApp, self).ready()
        from actstream import registry

        from .wizard_steps import WizardStepTags  # NOQA

        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )

        DocumentPageSearchResult = apps.get_model(
            app_label='documents', model_name='DocumentPageSearchResult'
        )

        DocumentTag = self.get_model('DocumentTag')
        Tag = self.get_model('Tag')

        Document.add_to_class(name='get_tags', value=method_get_tags)

        ModelAttribute(model=Document, name='get_tags')

        ModelEventType.register(
            model=Tag, event_types=(
                event_tag_attach, event_tag_created, event_tag_edited,
                event_tag_remove
            )
        )

        ModelField(
            Document, name='tags__label'
        )
        ModelField(
            Document, name='tags__color'
        )

        ModelPermission.register(
            model=Document, permissions=(
                permission_tag_attach, permission_tag_remove,
                permission_tag_view
            )
        )

        ModelPermission.register(
            model=Tag, permissions=(
                permission_acl_edit, permission_acl_view,
                permission_events_view, permission_tag_attach,
                permission_tag_delete, permission_tag_edit,
                permission_tag_remove, permission_tag_view,
            )
        )

        SourceColumn(
            attribute='label', is_identifier=True, is_sortable=True,
            source=DocumentTag,
        )
        SourceColumn(
            attribute='get_preview_widget', source=DocumentTag
        )

        SourceColumn(
            func=lambda context: widget_document_tags(
                document=context['object'], user=context['request'].user
            ), label=_('Tags'), source=Document
        )

        SourceColumn(
            func=lambda context: widget_document_tags(
                document=context['object'].document,
                user=context['request'].user
            ), label=_('Tags'), source=DocumentPageSearchResult
        )

        SourceColumn(
            attribute='label', is_identifier=True, is_sortable=True,
            source=Tag
        )
        SourceColumn(
            attribute='get_preview_widget', source=Tag
        )
        SourceColumn(
            func=lambda context: context['object'].get_document_count(
                user=context['request'].user
            ), label=_('Documents'), source=Tag
        )

        document_page_search.add_model_field(
            field='document_version__document__tags__label', label=_('Tags')
        )
        document_search.add_model_field(field='tags__label', label=_('Tags'))

        menu_facet.bind_links(
            links=(link_document_tag_list,), sources=(Document,)
        )

        menu_list_facet.bind_links(
            links=(
                link_acl_list, link_events_for_object,
                link_object_event_types_user_subcriptions_list,
                link_tag_tagged_item_list,
            ),
            sources=(Tag,)
        )

        menu_main.bind_links(links=(menu_tags,), position=98)

        menu_multi_item.bind_links(
            links=(
                link_multiple_documents_attach_tag,
                link_multiple_documents_tag_remove
            ),
            sources=(Document,)
        )
        menu_multi_item.bind_links(
            links=(link_tag_multiple_delete,), sources=(Tag,)
        )
        menu_object.bind_links(
            links=(
                link_tag_edit, link_tag_delete
            ),
            sources=(Tag,)
        )
        menu_sidebar.bind_links(
            links=(link_tag_attach, link_single_document_multiple_tag_remove),
            sources=(
                'tags:tag_attach', 'tags:document_tags',
                'tags:single_document_multiple_tag_remove'
            )
        )
        menu_tags.bind_links(
            links=(
                link_tag_list, link_tag_create
            )
        )

        registry.register(Tag)

        # Index update

        m2m_changed.connect(
            handler_index_document,
            dispatch_uid='tags_handler_index_document',
            sender=Tag.documents.through
        )

        pre_delete.connect(
            handler_tag_pre_delete,
            dispatch_uid='tags_handler_tag_pre_delete',
            sender=Tag
        )
