from __future__ import absolute_import, unicode_literals

from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation import Link

from .icons import (
    icon_comment_add, icon_comment_delete, icon_comments_for_document
)
from .permissions import (
    permission_comment_create, permission_comment_delete,
    permission_comment_view
)

link_comment_add = Link(
    args='object.pk', icon_class=icon_comment_add,
    permissions=(permission_comment_create,), text=_('Add comment'),
    view='comments:comment_add',
)
link_comment_delete = Link(
    args='object.pk', icon_class=icon_comment_delete,
    permissions=(permission_comment_delete,), tags='dangerous',
    text=_('Delete'), view='comments:comment_delete',
)
link_comments_for_document = Link(
    args='resolved_object.pk', icon_class=icon_comments_for_document,
    permissions=(permission_comment_view,), text=_('Comments'),
    view='comments:comments_for_document',
)
