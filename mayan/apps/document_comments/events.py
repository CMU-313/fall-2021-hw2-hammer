from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.events import EventTypeNamespace

namespace = EventTypeNamespace(
    label=_('Document comments'), name='document_comments'
)

event_document_comment_created = namespace.add_event_type(
    label=_('Document comment created'), name='create'
)
event_document_comment_deleted = namespace.add_event_type(
    label=_('Document comment deleted'), name='delete'
)
