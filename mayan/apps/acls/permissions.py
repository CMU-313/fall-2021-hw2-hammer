from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.permissions import PermissionNamespace

namespace = PermissionNamespace(label=_('Access control lists'), name='acls')

permission_acl_edit = namespace.add_permission(
    name='acl_edit', label=_('Edit ACLs')
)
permission_acl_view = namespace.add_permission(
    name='acl_view', label=_('View ACLs')
)
