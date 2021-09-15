from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation import Link
from mayan.apps.user_management.permissions import permission_group_edit

from .icons import (
    icon_role_create, icon_role_delete, icon_role_edit, icon_role_groups,
    icon_role_list, icon_role_permissions
)
from .permissions import (
    permission_role_create, permission_role_delete, permission_role_edit,
    permission_role_view
)

link_group_roles = Link(
    icon_class=icon_role_list, kwargs={'group_id': 'object.id'},
    permission=permission_group_edit, text=_('Roles'),
    view='permissions:group_roles',
)
link_permission_grant = Link(
    permission=permission_role_edit, text=_('Grant'),
    view='permissions:permission_multiple_grant'
)
link_permission_revoke = Link(
    permission=permission_role_edit, text=_('Revoke'),
    view='permissions:permission_multiple_revoke'
)
link_role_create = Link(
    icon_class=icon_role_create, permission=permission_role_create,
    text=_('Create new role'), view='permissions:role_create'
)
link_role_delete = Link(
    icon_class=icon_role_delete, kwargs={'role_id': 'object.id'},
    permission=permission_role_delete, tags='dangerous', text=_('Delete'),
    view='permissions:role_delete',
)
link_role_edit = Link(
    icon_class=icon_role_edit, kwargs={'role_id': 'object.id'},
    permission=permission_role_edit, text=_('Edit'),
    view='permissions:role_edit',
)
link_role_list = Link(
    icon_class=icon_role_list, permission=permission_role_view,
    text=_('Roles'), view='permissions:role_list'
)
link_role_groups = Link(
    icon_class=icon_role_groups, kwargs={'role_id': 'object.id'},
    permission=permission_role_edit, text=_('Groups'),
    view='permissions:role_groups',
)
link_role_permissions = Link(
    icon_class=icon_role_permissions, kwargs={'role_id': 'object.id'},
    permission=permission_role_edit, text=_('Role permissions'),
    view='permissions:role_permissions',
)
