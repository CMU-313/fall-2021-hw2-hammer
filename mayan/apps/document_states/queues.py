from django.utils.translation import ugettext_lazy as _

from mayan.apps.task_manager.classes import CeleryQueue
from mayan.apps.task_manager.workers import worker_fast, worker_slow

queue_document_states = CeleryQueue(
    label=_('Document states'), name='document_states', worker=worker_slow
)
queue_document_states_fast = CeleryQueue(
    label=_('Document states fast'), name='document_states_fast',
    worker=worker_fast
)

queue_document_states.add_task_type(
    label=_('Launch all workflows for all documents'),
    dotted_path='mayan.apps.document_states.tasks.task_launch_all_workflows'
)
queue_document_states.add_task_type(
    label=_('Launch a workflow'),
    dotted_path='mayan.apps.document_states.tasks.task_launch_workflow'
)
queue_document_states.add_task_type(
    label=_('Launch a workflow for a document'),
    dotted_path='mayan.apps.document_states.tasks.task_launch_workflow_for'
)
queue_document_states.add_task_type(
    label=_('Launch all workflows for a document'),
    dotted_path='mayan.apps.document_states.tasks.task_launch_all_workflow_for'
)
queue_document_states_fast.add_task_type(
    label=_('Generate workflow previews'),
    dotted_path='mayan.apps.document_states.tasks.task_generate_workflow_image'
)
