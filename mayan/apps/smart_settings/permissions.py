from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.permissions import PermissionNamespace

namespace = PermissionNamespace(label=_('Smart settings'), name='smart_settings')

permission_settings_edit = namespace.add_permission(
    name='permission_settings_edit', label=_('Edit settings')
)
permission_settings_view = namespace.add_permission(
    name='permission_settings_view', label=_('View settings')
)
