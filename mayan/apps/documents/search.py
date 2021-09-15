from __future__ import absolute_import, unicode_literals

from django.apps import apps
from django.db import connection
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.literals import LIST_MODE_CHOICE_ITEM
from mayan.apps.dynamic_search.classes import SearchModel

from .permissions import permission_document_view


def transformation_format_uuid(term_string):
    if connection.vendor in ('mysql', 'sqlite'):
        return term_string.replace('-', '')
    else:
        return term_string


def get_queryset_document_page_search_queryset():
    # Ignore documents in trash can
    DocumentPage = apps.get_model(
        app_label='documents', model_name='DocumentPage'
    )
    return DocumentPage.objects.filter(document__in_trash=False)


def get_queryset_document_version_page_search_queryset():
    # Ignore documents in trash can
    DocumentVersionPage = apps.get_model(
        app_label='documents', model_name='DocumentVersionPage'
    )
    return DocumentVersionPage.objects.filter(document_version__document__in_trash=False)


document_search = SearchModel(
    app_label='documents', list_mode=LIST_MODE_CHOICE_ITEM,
    model_name='Document', permission=permission_document_view,
    serializer_path='mayan.apps.documents.serializers.DocumentSerializer'
)
document_search.add_model_field(
    field='document_type__label', label=_('Document type')
)
document_search.add_model_field(
    field='versions__mimetype', label=_('MIME type')
)
document_search.add_model_field(field='label', label=_('Label'))
document_search.add_model_field(field='description', label=_('Description'))
document_search.add_model_field(
    field='uuid', label=_('UUID'),
    transformation_function=transformation_format_uuid
)
document_search.add_model_field(
    field='versions__checksum', label=_('Checksum')
)

document_page_search = SearchModel(
    app_label='documents', list_mode=LIST_MODE_CHOICE_ITEM,
    model_name='DocumentPage', permission=permission_document_view,
    queryset=get_queryset_document_page_search_queryset,
    serializer_path='mayan.apps.documents.serializers.DocumentPageSerializer'
)

document_version_page_search = SearchModel(
    app_label='documents', list_mode=LIST_MODE_CHOICE_ITEM,
    model_name='DocumentVersionPage', permission=permission_document_view,
    queryset=get_queryset_document_version_page_search_queryset,
    serializer_path='mayan.apps.documents.serializers.DocumentVersionPageSerializer'
)

document_page_search.add_model_field(
    field='document__document_type__label',
    label=_('Document type')
)
document_page_search.add_model_field(
    field='document__versions__mimetype',
    label=_('MIME type')
)
document_page_search.add_model_field(
    field='document__label', label=_('Label')
)
document_page_search.add_model_field(
    field='document__description', label=_('Description')
)
document_page_search.add_model_field(
    field='document__versions__checksum', label=_('Checksum')
)

document_version_page_search.add_model_field(
    field='document_version__document__document_type__label',
    label=_('Document type')
)
document_version_page_search.add_model_field(
    field='document_version__document__versions__mimetype',
    label=_('MIME type')
)
document_version_page_search.add_model_field(
    field='document_version__document__label', label=_('Label')
)
document_version_page_search.add_model_field(
    field='document_version__document__description', label=_('Description')
)
document_version_page_search.add_model_field(
    field='document_version__checksum', label=_('Checksum')
)
