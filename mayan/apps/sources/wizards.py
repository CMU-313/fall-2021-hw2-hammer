from __future__ import unicode_literals

from django.apps import apps
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.decorators import classonlymethod
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _

from formtools.wizard.views import SessionWizardView

from documents.forms import DocumentTypeSelectForm


class WizardStep(object):
    _registry = {}
    _deregistry = {}

    @classmethod
    def done(cls, wizard):
        return {}

    @classmethod
    def get(cls, name):
        return cls._registry[name]

    @classmethod
    def get_all(cls):
        return sorted(
            cls._registry.values(), key=lambda x: x.number
        )

    @classmethod
    def get_choices(cls, attribute_name):
        return [
            (step.name, getattr(step, attribute_name)) for step in cls.get_all()
        ]

    @classmethod
    def get_form_initial(cls, wizard):
        return {}

    @classmethod
    def get_form_kwargs(cls, wizard):
        return {}

    @classmethod
    def post_upload_process(cls, document, querystring=None):
        for step in cls.get_all():
            step.step_post_upload_process(
                document=document, querystring=querystring
            )

    @classmethod
    def register(cls, step):
        if step in cls._deregistry:
            # This step has been marked for reregistration before it was
            # registered
            return

        if step.name in cls._registry:
            raise Exception('A step with this name already exists: %s' % step.name)

        if step.number in [reigstered_step.number for reigstered_step in cls.get_all()]:
            raise Exception('A step with this number already exists: %s' % step.name)

        cls._registry[step.name] = step

    @classmethod
    def deregister(cls, step):
        try:
            cls._registry.pop(step.name)
        except KeyError:
            cls._deregistry[step.name] = step
        else:
            cls._deregistry[step.name] = step

    @classmethod
    def step_post_upload_process(cls, document, querystring=None):
        pass


class WizardStepDocumentType(WizardStep):
    form_class = DocumentTypeSelectForm
    label = _('Select document type')
    name = 'document_type_selection'
    number = 0

    @classmethod
    def condition(cls, wizard):
        return True

    @classmethod
    def done(cls, wizard):
        cleaned_data = wizard.get_cleaned_data_for_step(cls.name)
        if cleaned_data:
            return {
                'document_type_id': cleaned_data['document_type'].pk
            }

    @classmethod
    def get_form_kwargs(cls, wizard):
        return {'user': wizard.request.user}


WizardStep.register(WizardStepDocumentType)


class DocumentCreateWizard(SessionWizardView):
    template_name = 'appearance/generic_wizard.html'

    @classonlymethod
    def as_view(cls, *args, **kwargs):
        cls.form_list = WizardStep.get_choices(attribute_name='form_class')
        cls.condition_dict = dict(WizardStep.get_choices(attribute_name='condition'))
        return super(DocumentCreateWizard, cls).as_view(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        InteractiveSource = apps.get_model(
            app_label='sources', model_name='InteractiveSource'
        )

        form_list = WizardStep.get_choices(attribute_name='form_class')
        condition_dict = dict(WizardStep.get_choices(attribute_name='condition'))
        result = self.__class__.get_initkwargs(form_list=form_list, condition_dict=condition_dict)
        self.form_list = result['form_list']
        self.condition_dict = result['condition_dict']

        if not InteractiveSource.objects.filter(enabled=True).exists():
            messages.error(
                request,
                _(
                    'No interactive document sources have been defined or '
                    'none have been enabled, create one before proceeding.'
                )
            )
            return HttpResponseRedirect(reverse('sources:setup_source_list'))

        return super(
            DocumentCreateWizard, self
        ).dispatch(request, *args, **kwargs)

    def get_context_data(self, form, **kwargs):
        context = super(
            DocumentCreateWizard, self
        ).get_context_data(form=form, **kwargs)

        wizard_step = WizardStep.get(name=self.steps.current)

        context.update({
            'step_title': _(
                'Step %(step)d of %(total_steps)d: %(step_label)s'
            ) % {
                'step': self.steps.step1, 'total_steps': len(self.form_list),
                'step_label': wizard_step.label,
            },
            'submit_label': _('Next step'),
            'submit_icon': 'fa fa-arrow-right',
            'title': _('Document upload wizard'),
        })
        return context

    def get_form_initial(self, step):
        return WizardStep.get(name=step).get_form_initial(wizard=self) or {}

    def get_form_kwargs(self, step):
        return WizardStep.get(name=step).get_form_kwargs(wizard=self) or {}

    def done(self, form_list, **kwargs):
        query_dict = {}

        for step in WizardStep.get_all():
            query_dict.update(step.done(wizard=self) or {})

        url = '?'.join(
            [
                reverse('sources:upload_interactive'),
                urlencode(query_dict, doseq=True)
            ]
        )

        return HttpResponseRedirect(url)
