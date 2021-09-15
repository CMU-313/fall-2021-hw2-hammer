from __future__ import absolute_import, unicode_literals

import hashlib
import json
import logging

from furl import furl
from graphviz import Digraph

from django.apps import apps
from django.conf import settings
from django.core import serializers
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, models, transaction
from django.db.models import F, Max, Q
from django.urls import reverse
from django.utils.encoding import (
    force_bytes, force_text, python_2_unicode_compatible
)
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.models import AccessControlList
from mayan.apps.common.serialization import yaml_load
from mayan.apps.common.validators import YAMLValidator, validate_internal_name
from mayan.apps.documents.models import Document, DocumentType
from mayan.apps.documents.permissions import permission_document_view
from mayan.apps.events.models import StoredEventType

from .error_logs import error_log_state_actions
from .events import event_workflow_created, event_workflow_edited
from .literals import (
    FIELD_TYPE_CHOICES, WIDGET_CLASS_CHOICES, WORKFLOW_ACTION_WHEN_CHOICES,
    WORKFLOW_ACTION_ON_ENTRY, WORKFLOW_ACTION_ON_EXIT,
    WORKFLOW_IMAGE_CACHE_NAME
)
from .managers import WorkflowManager
from .permissions import permission_workflow_transition

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class Workflow(models.Model):
    """
    Fields:
    * label - Identifier. A name/label to call the workflow
    """
    internal_name = models.CharField(
        db_index=True, help_text=_(
            'This value will be used by other apps to reference this '
            'workflow. Can only contain letters, numbers, and underscores.'
        ), max_length=255, unique=True, validators=[validate_internal_name],
        verbose_name=_('Internal name')
    )
    label = models.CharField(
        max_length=255, unique=True, verbose_name=_('Label')
    )
    document_types = models.ManyToManyField(
        related_name='workflows', to=DocumentType, verbose_name=_(
            'Document types'
        )
    )

    objects = WorkflowManager()

    class Meta:
        ordering = ('label',)
        verbose_name = _('Workflow')
        verbose_name_plural = _('Workflows')

    def __str__(self):
        return self.label

    @cached_property
    def cache(self):
        Cache = apps.get_model(app_label='file_caching', model_name='Cache')
        return Cache.objects.get(name=WORKFLOW_IMAGE_CACHE_NAME)

    @cached_property
    def cache_partition(self):
        partition, created = self.cache.partitions.get_or_create(
            name='{}'.format(self.pk)
        )
        return partition

    def delete(self, *args, **kwargs):
        self.cache_partition.delete()
        return super(Workflow, self).delete(*args, **kwargs)

    def generate_image(self):
        cache_filename = '{}'.format(self.get_hash())

        if self.cache_partition.get_file(filename=cache_filename):
            logger.debug(
                'workflow cache file "%s" found', cache_filename
            )
        else:
            logger.debug(
                'workflow cache file "%s" not found', cache_filename
            )

            image = self.render()
            with self.cache_partition.create_file(filename=cache_filename) as file_object:
                file_object.write(image)

        return cache_filename

    def get_api_image_url(self, *args, **kwargs):
        final_url = furl()
        final_url.args = kwargs
        final_url.path = reverse(
            viewname='rest_api:workflow-image',
            kwargs={'pk': self.pk}
        )
        final_url.args['_hash'] = self.get_hash()

        return final_url.tostr()

    def get_document_types_not_in_workflow(self):
        return DocumentType.objects.exclude(pk__in=self.document_types.all())

    def get_hash(self):
        objects_lists = list(
            Workflow.objects.filter(pk=self.pk)
        ) + list(
            WorkflowState.objects.filter(workflow__pk=self.pk)
        ) + list(
            WorkflowStateAction.objects.filter(state__workflow__pk=self.pk)
        ) + list(
            WorkflowTransition.objects.filter(workflow__pk=self.pk)
        )

        return hashlib.sha256(
            force_bytes(
                serializers.serialize('json', objects_lists)
            )
        ).hexdigest()

    def get_initial_state(self):
        try:
            return self.states.get(initial=True)
        except self.states.model.DoesNotExist:
            return None
    get_initial_state.short_description = _('Initial state')

    def launch_for(self, document):
        try:
            logger.info(
                'Launching workflow %s for document %s', self, document
            )
            workflow_instance = self.instances.create(document=document)
            initial_state = self.get_initial_state()

            if initial_state:
                for action in initial_state.entry_actions.filter(enabled=True):
                    action.execute(context=workflow_instance.get_context())
        except IntegrityError:
            logger.info(
                'Workflow %s already launched for document %s', self, document
            )
        else:
            logger.info(
                'Workflow %s launched for document %s', self, document
            )

    def render(self):
        diagram = Digraph(
            name='finite_state_machine', graph_attr={
                'rankdir': 'LR', 'splines': 'polyline'
            }, format='png'
        )

        action_cache = {}
        state_cache = {}
        transition_cache = []

        for state in self.states.all():
            state_cache['s{}'.format(state.pk)] = {
                'name': 's{}'.format(state.pk),
                'label': state.label,
                'initial': state.initial,
                'connections': {'origin': 0, 'destination': 0}
            }

            for action in state.actions.all():
                action_cache['a{}'.format(action.pk)] = {
                    'name': 'a{}'.format(action.pk),
                    'label': action.label,
                    'state': 's{}'.format(state.pk),
                    'when': action.when,
                }

        for transition in self.transitions.all():
            transition_cache.append(
                {
                    'tail_name': 's{}'.format(transition.origin_state.pk),
                    'head_name': 's{}'.format(transition.destination_state.pk),
                    'label': transition.label
                }
            )
            state_cache['s{}'.format(transition.origin_state.pk)]['connections']['origin'] = state_cache['s{}'.format(transition.origin_state.pk)]['connections']['origin'] + 1
            state_cache['s{}'.format(transition.destination_state.pk)]['connections']['destination'] += 1

        for key, value in state_cache.items():
            kwargs = {
                'name': value['name'],
                'label': value['label'],
                'shape': 'doublecircle' if value['connections']['origin'] == 0 or value['connections']['destination'] == 0 or value['initial'] else 'circle',
                'style': 'filled' if value['initial'] else '',
                'fillcolor': '#eeeeee',
            }
            diagram.node(**kwargs)

        for transition in transition_cache:
            diagram.edge(**transition)

        for key, value in action_cache.items():
            kwargs = {
                'name': value['name'],
                'label': value['label'],
                'shape': 'box',
            }
            diagram.node(**kwargs)
            diagram.edge(
                **{
                    'head_name': '{}'.format(value['name']),
                    'tail_name': '{}'.format(value['state']),
                    'label': 'On entry' if value['when'] == WORKFLOW_ACTION_ON_ENTRY else 'On exit',
                    'arrowhead': 'dot',
                    'dir': 'both',
                    'arrowtail': 'dot',
                    'style': 'dashed',
                }
            )

        return diagram.pipe()

    def save(self, *args, **kwargs):
        _user = kwargs.pop('_user', None)
        created = not self.pk

        with transaction.atomic():
            result = super(Workflow, self).save(*args, **kwargs)

            if created:
                event_workflow_created.commit(actor=_user, target=self)
            else:
                event_workflow_edited.commit(actor=_user, target=self)

            return result


@python_2_unicode_compatible
class WorkflowState(models.Model):
    """
    Fields:
    * completion - Completion Amount - A user defined numerical value to help
    determine if the workflow of the document is nearing completion (100%).
    The Completion Amount will be determined by the completion value of the
    Actual State. Example: If the workflow has 3 states: registered, approved,
    archived; the admin could give the follow completion values to the
    states: 33%, 66%, 100%. If the Actual State of the document if approved,
    the Completion Amount will show 66%.
    """
    workflow = models.ForeignKey(
        on_delete=models.CASCADE, related_name='states', to=Workflow,
        verbose_name=_('Workflow')
    )
    label = models.CharField(max_length=255, verbose_name=_('Label'))
    initial = models.BooleanField(
        default=False,
        help_text=_(
            'Select if this will be the state with which you want the '
            'workflow to start in. Only one state can be the initial state.'
        ), verbose_name=_('Initial')
    )
    completion = models.IntegerField(
        blank=True, default=0, help_text=_(
            'Enter the percent of completion that this state represents in '
            'relation to the workflow. Use numbers without the percent sign.'
        ), verbose_name=_('Completion')
    )

    class Meta:
        ordering = ('label',)
        unique_together = ('workflow', 'label')
        verbose_name = _('Workflow state')
        verbose_name_plural = _('Workflow states')

    def __str__(self):
        return self.label

    @property
    def entry_actions(self):
        return self.actions.filter(when=WORKFLOW_ACTION_ON_ENTRY)

    @property
    def exit_actions(self):
        return self.actions.filter(when=WORKFLOW_ACTION_ON_EXIT)

    def get_documents(self):
        latest_entries = WorkflowInstanceLogEntry.objects.annotate(
            max_datetime=Max(
                'workflow_instance__log_entries__datetime'
            )
        ).filter(
            datetime=F('max_datetime')
        )

        state_latest_entries = latest_entries.filter(
            transition__destination_state=self
        )

        return Document.objects.filter(
            Q(
                workflows__pk__in=state_latest_entries.values_list(
                    'workflow_instance', flat=True
                )
            ) | Q(
                workflows__log_entries__isnull=True,
                workflows__workflow__states=self,
                workflows__workflow__states__initial=True
            )
        ).distinct()

    def save(self, *args, **kwargs):
        # Solve issue #557 "Break workflows with invalid input"
        # without using a migration.
        # Remove blank=True, remove this, and create a migration in the next
        # minor version.

        try:
            self.completion = int(self.completion)
        except (TypeError, ValueError):
            self.completion = 0

        if self.initial:
            self.workflow.states.all().update(initial=False)
        return super(WorkflowState, self).save(*args, **kwargs)


@python_2_unicode_compatible
class WorkflowStateAction(models.Model):
    state = models.ForeignKey(
        on_delete=models.CASCADE, related_name='actions', to=WorkflowState,
        verbose_name=_('Workflow state')
    )
    label = models.CharField(
        max_length=255, help_text=_('A simple identifier for this action.'),
        verbose_name=_('Label')
    )
    enabled = models.BooleanField(default=True, verbose_name=_('Enabled'))
    when = models.PositiveIntegerField(
        choices=WORKFLOW_ACTION_WHEN_CHOICES,
        default=WORKFLOW_ACTION_ON_ENTRY, help_text=_(
            'At which moment of the state this action will execute'
        ), verbose_name=_('When')
    )
    action_path = models.CharField(
        max_length=128, help_text=_(
            'The dotted Python path to the workflow action class to execute.'
        ), verbose_name=_('Entry action path')
    )
    action_data = models.TextField(
        blank=True, verbose_name=_('Entry action data')
    )

    class Meta:
        ordering = ('label',)
        unique_together = ('state', 'label')
        verbose_name = _('Workflow state action')
        verbose_name_plural = _('Workflow state actions')

    def __str__(self):
        return self.label

    def dumps(self, data):
        self.action_data = json.dumps(data)
        self.save()

    def execute(self, context):
        try:
            self.get_class_instance().execute(context=context)
        except Exception as exception:
            error_log_state_actions.create(
                obj=self, result='{}; {}'.format(
                    exception.__class__.__name__, exception
                )
            )

            if settings.DEBUG:
                raise

    def get_class(self):
        return import_string(self.action_path)

    def get_class_instance(self):
        return self.get_class()(form_data=self.loads())

    def get_class_label(self):
        return self.get_class().label

    def loads(self):
        return json.loads(self.action_data)


@python_2_unicode_compatible
class WorkflowTransition(models.Model):
    workflow = models.ForeignKey(
        on_delete=models.CASCADE, related_name='transitions', to=Workflow,
        verbose_name=_('Workflow')
    )
    label = models.CharField(max_length=255, verbose_name=_('Label'))
    origin_state = models.ForeignKey(
        on_delete=models.CASCADE, related_name='origin_transitions',
        to=WorkflowState, verbose_name=_('Origin state')
    )
    destination_state = models.ForeignKey(
        on_delete=models.CASCADE, related_name='destination_transitions',
        to=WorkflowState, verbose_name=_('Destination state')
    )

    class Meta:
        ordering = ('label',)
        unique_together = (
            'workflow', 'label', 'origin_state', 'destination_state'
        )
        verbose_name = _('Workflow transition')
        verbose_name_plural = _('Workflow transitions')

    def __str__(self):
        return self.label


@python_2_unicode_compatible
class WorkflowTransitionField(models.Model):
    transition = models.ForeignKey(
        on_delete=models.CASCADE, related_name='fields',
        to=WorkflowTransition, verbose_name=_('Transition')
    )
    field_type = models.PositiveIntegerField(
        choices=FIELD_TYPE_CHOICES, verbose_name=_('Type')
    )
    name = models.CharField(
        help_text=_(
            'The name that will be used to identify this field in other parts '
            'of the workflow system.'
        ), max_length=128, verbose_name=_('Internal name')
    )
    label = models.CharField(
        help_text=_(
            'The field name that will be shown on the user interface.'
        ), max_length=128, verbose_name=_('Label'))
    help_text = models.TextField(
        blank=True, help_text=_(
            'An optional message that will help users better understand the '
            'purpose of the field and data to provide.'
        ), verbose_name=_('Help text')
    )
    required = models.BooleanField(
        default=False, help_text=_(
            'Whether this fields needs to be filled out or not to proceed.'
        ), verbose_name=_('Required')
    )
    widget = models.PositiveIntegerField(
        blank=True, choices=WIDGET_CLASS_CHOICES, help_text=_(
            'An optional class to change the default presentation of the field.'
        ), null=True, verbose_name=_('Widget class')
    )
    widget_kwargs = models.TextField(
        blank=True, help_text=_(
            'A group of keyword arguments to customize the widget. '
            'Use YAML format.'
        ), validators=[YAMLValidator()],
        verbose_name=_('Widget keyword arguments')
    )

    class Meta:
        unique_together = ('transition', 'name')
        verbose_name = _('Workflow transition trigger event')
        verbose_name_plural = _('Workflow transitions trigger events')

    def __str__(self):
        return self.label

    def get_widget_kwargs(self):
        return yaml_load(stream=self.widget_kwargs)


@python_2_unicode_compatible
class WorkflowTransitionTriggerEvent(models.Model):
    transition = models.ForeignKey(
        on_delete=models.CASCADE, related_name='trigger_events',
        to=WorkflowTransition, verbose_name=_('Transition')
    )
    event_type = models.ForeignKey(
        on_delete=models.CASCADE, to=StoredEventType,
        verbose_name=_('Event type')
    )

    class Meta:
        verbose_name = _('Workflow transition trigger event')
        verbose_name_plural = _('Workflow transitions trigger events')

    def __str__(self):
        return force_text(self.transition)


@python_2_unicode_compatible
class WorkflowInstance(models.Model):
    workflow = models.ForeignKey(
        on_delete=models.CASCADE, related_name='instances', to=Workflow,
        verbose_name=_('Workflow')
    )
    document = models.ForeignKey(
        on_delete=models.CASCADE, related_name='workflows', to=Document,
        verbose_name=_('Document')
    )
    context = models.TextField(
        blank=True, verbose_name=_('Context')
    )

    class Meta:
        ordering = ('workflow',)
        unique_together = ('document', 'workflow')
        verbose_name = _('Workflow instance')
        verbose_name_plural = _('Workflow instances')

    def __str__(self):
        return force_text(self.workflow)

    def do_transition(self, transition, extra_data=None, user=None, comment=None):
        with transaction.atomic():
            try:
                if transition in self.get_current_state().origin_transitions.all():
                    if extra_data:
                        context = self.loads()
                        context.update(extra_data)
                        self.dumps(context=context)

                    self.log_entries.create(
                        comment=comment or '',
                        extra_data=json.dumps(extra_data or {}),
                        transition=transition, user=user
                    )
            except AttributeError:
                # No initial state has been set for this workflow
                pass

    def dumps(self, context):
        """
        Serialize the context data.
        """
        self.context = json.dumps(context)
        self.save()

    def get_absolute_url(self):
        return reverse(
            viewname='document_states:workflow_instance_detail', kwargs={
                'pk': self.pk
            }
        )

    def get_context(self):
        context = {
            'document': self.document, 'workflow': self.workflow,
            'workflow_instance': self,
        }
        context['workflow_instance_context'] = self.loads()
        return context

    def get_current_state(self):
        """
        Actual State - The current state of the workflow. If there are
        multiple states available, for example: registered, approved,
        archived; this field will tell at the current state where the
        document is right now.
        """
        try:
            return self.get_last_transition().destination_state
        except AttributeError:
            return self.workflow.get_initial_state()

    def get_last_log_entry(self):
        try:
            return self.log_entries.order_by('datetime').last()
        except AttributeError:
            return None

    def get_last_transition(self):
        """
        Last Transition - The last transition used by the last user to put
        the document in the actual state.
        """
        try:
            return self.get_last_log_entry().transition
        except AttributeError:
            return None

    def get_transition_choices(self, _user=None):
        current_state = self.get_current_state()

        if current_state:
            queryset = current_state.origin_transitions.all()

            if _user:
                try:
                    """
                    Check for ACL access to the workflow, if true, allow
                    all transition options.
                    """
                    AccessControlList.objects.check_access(
                        obj=self.workflow,
                        permissions=(permission_workflow_transition,),
                        user=_user
                    )
                except PermissionDenied:
                    """
                    If not ACL access to the workflow, filter transition
                    options by each transition ACL access
                    """
                    queryset = AccessControlList.objects.restrict_queryset(
                        permission=permission_workflow_transition,
                        queryset=queryset,
                        user=_user
                    )
            return queryset
        else:
            """
            This happens when a workflow has no initial state and a document
            whose document type has this workflow is created. We return an
            empty transition queryset.
            """
            return WorkflowTransition.objects.none()

    def loads(self):
        """
        Deserialize the context data.
        """
        return json.loads(self.context or '{}')


@python_2_unicode_compatible
class WorkflowInstanceLogEntry(models.Model):
    """
    Fields:
    * user - The user who last transitioned the document from a state to the
    Actual State.
    * datetime - Date Time - The date and time when the last user transitioned
    the document state to the Actual state.
    """
    workflow_instance = models.ForeignKey(
        on_delete=models.CASCADE, related_name='log_entries',
        to=WorkflowInstance, verbose_name=_('Workflow instance')
    )
    datetime = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name=_('Datetime')
    )
    transition = models.ForeignKey(
        on_delete=models.CASCADE, to=WorkflowTransition,
        verbose_name=_('Transition')
    )
    user = models.ForeignKey(
        blank=True, null=True, on_delete=models.CASCADE,
        to=settings.AUTH_USER_MODEL, verbose_name=_('User')
    )
    comment = models.TextField(blank=True, verbose_name=_('Comment'))
    extra_data = models.TextField(blank=True, verbose_name=_('Extra data'))

    class Meta:
        ordering = ('datetime',)
        verbose_name = _('Workflow instance log entry')
        verbose_name_plural = _('Workflow instance log entries')

    def __str__(self):
        return force_text(self.transition)

    def clean(self):
        if self.transition not in self.workflow_instance.get_transition_choices(_user=self.user):
            raise ValidationError(_('Not a valid transition choice.'))

    def get_extra_data(self):
        result = {}
        for key, value in self.loads().items():
            result[self.transition.fields.get(name=key).label] = value

        return result

    def loads(self):
        """
        Deserialize the context data.
        """
        return json.loads(self.extra_data or '{}')

    def save(self, *args, **kwargs):
        with transaction.atomic():
            result = super(WorkflowInstanceLogEntry, self).save(*args, **kwargs)
            context = self.workflow_instance.get_context()
            context.update(
                {
                    'entry_log': self
                }
            )

            for action in self.transition.origin_state.exit_actions.filter(enabled=True):
                context.update(
                    {
                        'action': action,
                    }
                )
                action.execute(context=context)

            for action in self.transition.destination_state.entry_actions.filter(enabled=True):
                context.update(
                    {
                        'action': action,
                    }
                )
                action.execute(context=context)

            return result


class WorkflowRuntimeProxy(Workflow):
    class Meta:
        proxy = True
        verbose_name = _('Workflow runtime proxy')
        verbose_name_plural = _('Workflow runtime proxies')

    def get_document_count(self, user):
        """
        Return the numeric count of documents executing this workflow.
        The count is filtered by access.
        """
        return AccessControlList.objects.restrict_queryset(
            permission=permission_document_view,
            queryset=Document.objects.filter(workflows__workflow=self),
            user=user
        ).count()


class WorkflowStateRuntimeProxy(WorkflowState):
    class Meta:
        proxy = True
        verbose_name = _('Workflow state runtime proxy')
        verbose_name_plural = _('Workflow state runtime proxies')

    def get_document_count(self, user):
        """
        Return the numeric count of documents at this workflow state.
        The count is filtered by access.
        """
        return AccessControlList.objects.restrict_queryset(
            permission=permission_document_view, queryset=self.get_documents(),
            user=user
        ).count()
