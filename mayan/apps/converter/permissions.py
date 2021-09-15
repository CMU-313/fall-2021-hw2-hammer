from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.permissions import PermissionNamespace

namespace = PermissionNamespace(label=_('Converter'), name='converter')

permission_transformation_create = namespace.add_permission(
    name='transformation_create', label=_('Create new transformations')
)
permission_transformation_delete = namespace.add_permission(
    name='transformation_delete', label=_('Delete transformations')
)
permission_transformation_edit = namespace.add_permission(
    name='transformation_edit', label=_('Edit transformations')
)
permission_transformation_view = namespace.add_permission(
    name='transformation_view', label=_('View existing transformations')
)
