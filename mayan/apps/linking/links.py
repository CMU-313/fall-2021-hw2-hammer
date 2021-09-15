from django.utils.translation import ugettext_lazy as _

from mayan.apps.documents.permissions import (
    permission_document_type_edit, permission_document_view
)
from mayan.apps.navigation.classes import Link


from .permissions import (
    permission_smart_link_create, permission_smart_link_delete,
    permission_smart_link_edit, permission_smart_link_view
)


link_document_type_smart_links = Link(
    args='resolved_object.pk',
    icon_class_path='mayan.apps.linking.icons.icon_document_type_smart_links',
    permissions=(permission_document_type_edit,), text=_('Smart links'),
    view='linking:document_type_smart_links',
)
link_smart_link_condition_create = Link(
    args='object.pk',
    icon_class_path='mayan.apps.linking.icons.icon_smart_link_condition_create',
    permissions=(permission_smart_link_edit,), text=_('Create condition'),
    view='linking:smart_link_condition_create',
)
link_smart_link_condition_delete = Link(
    args='resolved_object.pk',
    icon_class_path='mayan.apps.linking.icons.icon_smart_link_condition_delete',
    permissions=(permission_smart_link_edit,),
    tags='dangerous', text=_('Delete'),
    view='linking:smart_link_condition_delete',
)
link_smart_link_condition_edit = Link(
    args='resolved_object.pk',
    icon_class_path='mayan.apps.linking.icons.icon_smart_link_condition_edit',
    permissions=(permission_smart_link_edit,),
    text=_('Edit'), view='linking:smart_link_condition_edit',
)
link_smart_link_condition_list = Link(
    args='object.pk',
    icon_class_path='mayan.apps.linking.icons.icon_smart_link_condition_list',
    permissions=(permission_smart_link_edit,),
    text=_('Conditions'), view='linking:smart_link_condition_list',
)
link_smart_link_create = Link(
    icon_class_path='mayan.apps.linking.icons.icon_smart_link_create',
    permissions=(permission_smart_link_create,),
    text=_('Create new smart link'), view='linking:smart_link_create'
)
link_smart_link_delete = Link(
    args='object.pk',
    icon_class_path='mayan.apps.linking.icons.icon_smart_link_delete',
    permissions=(permission_smart_link_delete,),
    tags='dangerous', text=_('Delete'), view='linking:smart_link_delete',
)
link_smart_link_document_types = Link(
    args='object.pk',
    icon_class_path='mayan.apps.linking.icons.icon_smart_link_document_types',
    permissions=(permission_smart_link_edit,),
    text=_('Document types'), view='linking:smart_link_document_types',
)
link_smart_link_edit = Link(
    args='object.pk',
    icon_class_path='mayan.apps.linking.icons.icon_smart_link_edit',
    permissions=(permission_smart_link_edit,),
    text=_('Edit'), view='linking:smart_link_edit',
)
link_smart_link_instance_view = Link(
    args=('document.pk', 'object.pk',),
    permissions=(permission_smart_link_view,), text=_('Documents'),
    view='linking:smart_link_instance_view',
)
link_smart_link_instances_for_document = Link(
    args='resolved_object.pk',
    icon_class_path='mayan.apps.linking.icons.icon_smart_link_instances_for_document',
    permissions=(permission_document_view,), text=_('Smart links'),
    view='linking:smart_link_instances_for_document',
)
link_smart_link_list = Link(
    icon_class_path='mayan.apps.linking.icons.icon_smart_link_list',
    permissions=(permission_smart_link_create,), text=_('Smart links'),
    view='linking:smart_link_list'
)
link_smart_link_setup = Link(
    icon_class_path='mayan.apps.linking.icons.icon_smart_link_setup',
    permissions=(permission_smart_link_create,), text=_('Smart links'),
    view='linking:smart_link_list'
)
