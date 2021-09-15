from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.permissions import PermissionNamespace

namespace = PermissionNamespace(label=_('Sources setup'), name='source_setup')

permission_sources_setup_create = namespace.add_permission(
    name='sources_setup_create', label=_('Create new document sources')
)
permission_sources_setup_delete = namespace.add_permission(
    name='sources_setup_delete', label=_('Delete document sources')
)
permission_sources_setup_edit = namespace.add_permission(
    name='sources_setup_edit', label=_('Edit document sources')
)
permission_sources_setup_view = namespace.add_permission(
    name='sources_setup_view', label=_('View existing document sources')
)
permission_staging_file_delete = namespace.add_permission(
    name='sources_staging_file_delete', label=_('Delete staging files')
)
