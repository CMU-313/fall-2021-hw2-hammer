from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from mayan.apps.document_indexing.tasks import task_index_document
from mayan.apps.events.classes import EventType

from .literals import STORAGE_NAME_WORKFLOW_CACHE
from .settings import setting_workflow_image_cache_maximum_size
from .tasks import task_launch_all_workflow_for


def handler_create_workflow_image_cache(sender, **kwargs):
    Cache = apps.get_model(app_label='file_caching', model_name='Cache')
    Cache.objects.update_or_create(
        defaults={
            'maximum_size': setting_workflow_image_cache_maximum_size.value,
        }, defined_storage_name=STORAGE_NAME_WORKFLOW_CACHE,
    )


def handler_index_document(sender, **kwargs):
    task_index_document.apply_async(
        kwargs=dict(
            document_id=kwargs['instance'].workflow_instance.document.pk
        )
    )


def handler_launch_workflow(sender, instance, created, **kwargs):
    if created:
        task_launch_all_workflow_for.apply_async(
            kwargs={'document_id': instance.pk}
        )


def handler_trigger_transition(sender, **kwargs):
    action = kwargs['instance']

    Document = apps.get_model(
        app_label='documents', model_name='Document'
    )
    WorkflowInstance = apps.get_model(
        app_label='document_states', model_name='WorkflowInstance'
    )
    WorkflowTransition = apps.get_model(
        app_label='document_states', model_name='WorkflowTransition'
    )

    trigger_transitions = WorkflowTransition.objects.filter(
        trigger_events__event_type__name=kwargs['instance'].verb
    )

    if isinstance(action.target, Document):
        workflow_instances = WorkflowInstance.objects.filter(
            workflow__transitions__in=trigger_transitions, document=action.target
        ).distinct()
    elif isinstance(action.action_object, Document):
        workflow_instances = WorkflowInstance.objects.filter(
            workflow__transitions__in=trigger_transitions, document=action.action_object
        ).distinct()
    else:
        workflow_instances = WorkflowInstance.objects.none()

    for workflow_instance in workflow_instances:
        # Select the first transition that is valid for this workflow state
        valid_transitions = list(
            set(trigger_transitions) & set(workflow_instance.get_transition_choices())
        )
        if valid_transitions:
            workflow_instance.do_transition(
                comment=_('Event trigger: %s') % EventType.get(name=action.verb).label,
                transition=valid_transitions[0]
            )
