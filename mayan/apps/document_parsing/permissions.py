from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.permissions import PermissionNamespace

namespace = PermissionNamespace(label=_('Document parsing'), name='document_parsing')

permission_content_view = namespace.add_permission(
    name='content_view', label=_('View the content of a document')
)
permission_document_type_parsing_setup = namespace.add_permission(
    name='document_type_setup',
    label=_('Change document type parsing settings')
)
permission_parse_document = namespace.add_permission(
    name='parse_document', label=_('Parse the content of a document')
)
