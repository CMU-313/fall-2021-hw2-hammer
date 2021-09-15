from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from documents.permissions import permission_document_type_edit
from navigation import Link

from .icons import icon_metadata_view
from .permissions import (
    permission_metadata_document_add, permission_metadata_document_edit,
    permission_metadata_document_remove, permission_metadata_document_view,
    permission_metadata_type_create, permission_metadata_type_delete,
    permission_metadata_type_edit, permission_metadata_type_view
)

link_metadata_add = Link(
    args='object.pk', permissions=(permission_metadata_document_add,),
    text=_('Add metadata'), view='metadata:metadata_add',
)
link_metadata_edit = Link(
    args='object.pk', permissions=(permission_metadata_document_edit,),
    text=_('Edit metadata'), view='metadata:metadata_edit'
)
link_metadata_multiple_add = Link(
    text=_('Add metadata'), view='metadata:metadata_multiple_add'
)
link_metadata_multiple_edit = Link(
    text=_('Edit metadata'), view='metadata:metadata_multiple_edit'
)
link_metadata_multiple_remove = Link(
    text=_('Remove metadata'), view='metadata:metadata_multiple_remove'
)
link_metadata_remove = Link(
    args='object.pk', permissions=(permission_metadata_document_remove,),
    text=_('Remove metadata'), view='metadata:metadata_remove',
)
link_metadata_view = Link(
    args='resolved_object.pk', icon_class=icon_metadata_view,
    permissions=(permission_metadata_document_view,), text=_('Metadata'),
    view='metadata:metadata_view',
)
link_setup_document_type_metadata_types = Link(
    args='resolved_object.pk', permissions=(permission_document_type_edit,),
    text=_('Metadata types'), view='metadata:setup_document_type_metadata_types',
)
link_setup_metadata_type_document_types = Link(
    args='resolved_object.pk', permissions=(permission_document_type_edit,),
    text=_('Document types'), view='metadata:setup_metadata_type_document_types',
)
link_setup_metadata_type_create = Link(
    permissions=(permission_metadata_type_create,), text=_('Create new'),
    view='metadata:setup_metadata_type_create'
)
link_setup_metadata_type_delete = Link(
    args='object.pk', permissions=(permission_metadata_type_delete,),
    tags='dangerous', text=_('Delete'), view='metadata:setup_metadata_type_delete',
)
link_setup_metadata_type_edit = Link(
    args='object.pk', permissions=(permission_metadata_type_edit,),
    text=_('Edit'), view='metadata:setup_metadata_type_edit'
)
link_setup_metadata_type_list = Link(
    icon_class=icon_metadata_view, permissions=(permission_metadata_type_view,),
    text=_('Metadata types'), view='metadata:setup_metadata_type_list'
)
