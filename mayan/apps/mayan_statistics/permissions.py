from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.permissions import PermissionNamespace

namespace = PermissionNamespace(label=_('Statistics'), name='statistics')

permission_statistics_view = namespace.add_permission(
    name='statistics_view', label=_('View statistics')
)
