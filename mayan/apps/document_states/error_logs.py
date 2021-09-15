from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.classes import ErrorLogNamespace

error_log_state_actions = ErrorLogNamespace(
    name='workflow_state_actions', label=_('Workflow state actions')
)
