from django.apps import apps
from django.db.models.signals import m2m_changed, pre_delete
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.classes import ModelPermission
from mayan.apps.acls.links import link_acl_list
from mayan.apps.acls.permissions import permission_acl_edit, permission_acl_view
from mayan.apps.common.apps import MayanAppConfig
from mayan.apps.common.classes import (
    ModelCopy, ModelFieldRelated, ModelQueryFields
)
from mayan.apps.common.menus import (
    menu_facet, menu_list_facet, menu_main, menu_multi_item, menu_object,
    menu_secondary
)
from mayan.apps.events.classes import EventModelRegistry, ModelEventType
from mayan.apps.events.permissions import permission_events_view
from mayan.apps.navigation.classes import SourceColumn

from .events import (
    event_tag_attached, event_tag_edited, event_tag_removed
)
from .handlers import handler_index_document, handler_tag_pre_delete
from .html_widgets import DocumentTagWidget
from .links import (
    link_document_tag_list, link_document_multiple_tag_multiple_attach,
    link_document_multiple_tag_multiple_remove,
    link_document_tag_multiple_remove, link_document_tag_multiple_attach, link_tag_create,
    link_tag_delete, link_tag_edit, link_tag_list,
    link_tag_multiple_delete, link_tag_document_list
)
from .menus import menu_tags
from .methods import method_document_get_tags
from .permissions import (
    permission_tag_attach, permission_tag_delete, permission_tag_edit,
    permission_tag_remove, permission_tag_view
)


class TagsApp(MayanAppConfig):
    app_namespace = 'tags'
    app_url = 'tags'
    has_rest_api = True
    has_static_media = True
    has_tests = True
    name = 'mayan.apps.tags'
    verbose_name = _('Tags')

    def ready(self):
        super().ready()
        Document = apps.get_model(
            app_label='documents', model_name='Document'
        )

        DocumentFileSearchResult = apps.get_model(
            app_label='documents', model_name='DocumentFileSearchResult'
        )
        DocumentFilePageSearchResult = apps.get_model(
            app_label='documents', model_name='DocumentFilePageSearchResult'
        )
        DocumentVersionSearchResult = apps.get_model(
            app_label='documents', model_name='DocumentVersionSearchResult'
        )
        DocumentVersionPageSearchResult = apps.get_model(
            app_label='documents', model_name='DocumentVersionPageSearchResult'
        )

        DocumentTag = self.get_model(model_name='DocumentTag')
        Tag = self.get_model(model_name='Tag')

        Document.add_to_class(name='get_tags', value=method_document_get_tags)

        EventModelRegistry.register(model=Tag)

        ModelCopy(
            model=Tag, bind_link=True, register_permission=True
        ).add_fields(
            field_names=(
                'label', 'color', 'documents',
            ),
        )

        ModelEventType.register(
            model=Tag, event_types=(
                event_tag_attached, event_tag_edited, event_tag_removed
            )
        )

        ModelFieldRelated(model=Document, name='tags__label')
        ModelFieldRelated(model=Document, name='tags__color')

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

        model_query_fields_document = ModelQueryFields.get(model=Document)
        model_query_fields_document.add_prefetch_related_field(field_name='tags')

        model_query_fields_tag = ModelQueryFields.get(model=Tag)
        model_query_fields_tag.add_prefetch_related_field(field_name='documents')

        SourceColumn(
            attribute='label', is_identifier=True, is_sortable=True,
            source=DocumentTag
        )

        SourceColumn(
            label=_('Tags'), source=Document, widget=DocumentTagWidget
        )

        SourceColumn(
            attribute='document', label=_('Tags'),
            source=DocumentFileSearchResult, widget=DocumentTagWidget
        )
        SourceColumn(
            attribute='document_file__document', label=_('Tags'),
            source=DocumentFilePageSearchResult, widget=DocumentTagWidget
        )

        SourceColumn(
            attribute='document', label=_('Tags'),
            source=DocumentVersionSearchResult, widget=DocumentTagWidget
        )
        SourceColumn(
            attribute='document_version__document', label=_('Tags'),
            source=DocumentVersionPageSearchResult, widget=DocumentTagWidget
        )

        SourceColumn(
            attribute='label', is_identifier=True, is_sortable=True,
            source=Tag
        )
        SourceColumn(
            attribute='get_preview_widget', include_label=True, source=Tag
        )
        source_column_tag_document_count = SourceColumn(
            func=lambda context: context['object'].get_document_count(
                user=context['request'].user
            ), include_label=True, label=_('Documents'), source=Tag
        )
        source_column_tag_document_count.add_exclude(source=DocumentTag)

        menu_facet.bind_links(
            links=(link_document_tag_list,), sources=(Document,)
        )

        menu_list_facet.bind_links(
            links=(
                link_acl_list, link_tag_document_list,
            ), sources=(Tag,)
        )

        menu_tags.bind_links(
            links=(
                link_tag_list, link_tag_create
            )
        )

        menu_main.bind_links(links=(menu_tags,), position=98)

        menu_multi_item.bind_links(
            links=(
                link_document_multiple_tag_multiple_attach,
                link_document_multiple_tag_multiple_remove
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
        menu_secondary.bind_links(
            links=(link_document_tag_multiple_attach, link_document_tag_multiple_remove),
            sources=(
                'tags:tag_attach', 'tags:document_tag_list',
                'tags:single_document_multiple_tag_remove'
            )
        )

        # Index update

        m2m_changed.connect(
            dispatch_uid='tags_handler_index_document',
            receiver=handler_index_document,
            sender=Tag.documents.through
        )

        pre_delete.connect(
            dispatch_uid='tags_handler_tag_pre_delete',
            receiver=handler_tag_pre_delete,
            sender=Tag
        )
