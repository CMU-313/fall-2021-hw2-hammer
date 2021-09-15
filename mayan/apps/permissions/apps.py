from __future__ import unicode_literals

from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls import ModelPermission
from mayan.apps.acls.links import link_acl_list
from mayan.apps.acls.permissions import permission_acl_edit, permission_acl_view
from mayan.apps.common import (
    MayanAppConfig, menu_list_facet, menu_multi_item, menu_object,
    menu_secondary, menu_setup
)
from mayan.apps.common.signals import perform_upgrade
from mayan.apps.navigation import SourceColumn

from .handlers import handler_purge_permissions
from .links import (
    link_group_roles, link_permission_grant, link_permission_revoke,
    link_role_create, link_role_delete, link_role_edit, link_role_groups,
    link_role_list, link_role_permissions
)
from .permissions import (
    permission_permission_grant, permission_permission_revoke,
    permission_role_delete, permission_role_edit, permission_role_view
)
from .search import *  # NOQA


class PermissionsApp(MayanAppConfig):
    app_namespace = 'permissions'
    app_url = 'permissions'
    has_rest_api = True
    has_tests = True
    name = 'mayan.apps.permissions'
    verbose_name = _('Permissions')

    def ready(self):
        super(PermissionsApp, self).ready()

        Role = self.get_model('Role')
        Group = apps.get_model(app_label='auth', model_name='Group')

        ModelPermission.register(
            model=Role, permissions=(
                permission_acl_edit, permission_acl_view,
                permission_permission_grant, permission_permission_revoke,
                permission_role_delete, permission_role_edit,
                permission_role_view
            )
        )

        SourceColumn(attribute='label', is_identifier=True, source=Role)

        menu_list_facet.bind_links(
            links=(
                link_acl_list, link_role_groups, link_role_permissions,
            ), sources=(Role,)
        )
        menu_list_facet.bind_links(
            links=(link_group_roles,), sources=(Group,)
        )
        menu_object.bind_links(
            links=(
                link_role_edit, link_role_delete
            ), sources=(Role,)
        )
        menu_multi_item.bind_links(
            links=(link_permission_grant, link_permission_revoke),
            sources=('permissions:role_permissions',)
        )
        menu_secondary.bind_links(
            links=(link_role_list, link_role_create),
            sources=(Role, 'permissions:role_create', 'permissions:role_list')
        )
        menu_setup.bind_links(links=(link_role_list,))

        perform_upgrade.connect(
            dispatch_uid='permissions_handler_purge_permissions',
            receiver=handler_purge_permissions
        )
