from django.utils.translation import ugettext_lazy as _

from mayan.apps.converter.classes import Layer

from .permissions import (
    permission_redaction_create, permission_redaction_delete,
    permission_redaction_edit, permission_redaction_exclude,
    permission_redaction_view
)

layer_redactions = Layer(
    empty_results_text=_(
        'Redactions allow removing access to confidential and '
        'sensitive information without having to modify the document.'
    ), label=_('Redactions'), name='redactions',
    order=0, permissions={
        'create': permission_redaction_create,
        'delete': permission_redaction_delete,
        'exclude': permission_redaction_exclude,
        'edit': permission_redaction_edit,
        'select': permission_redaction_create,
        'view': permission_redaction_view,
    }, symbol='highlighter'
)
