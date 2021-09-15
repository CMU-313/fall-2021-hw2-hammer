import logging

from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.models import AccessControlList
from mayan.apps.document_states.classes import WorkflowAction

from .models import Cabinet
from .permissions import (
    permission_cabinet_add_document, permission_cabinet_remove_document
)

__all__ = ('CabinetAddAction', 'CabinetRemoveAction')
logger = logging.getLogger(name=__name__)


class CabinetAddAction(WorkflowAction):
    fields = {
        'cabinets': {
            'label': _('Cabinets'),
            'class': 'django.forms.ModelMultipleChoiceField', 'kwargs': {
                'help_text': _(
                    'Cabinets to which the document will be added.'
                ),
                'queryset': Cabinet.objects.none(), 'required': False
            }
        },
    }
    label = _('Add to cabinets')
    widgets = {
        'cabinets': {
            'class': 'django.forms.widgets.SelectMultiple', 'kwargs': {
                'attrs': {'class': 'select2'},
            }
        }
    }
    permission = permission_cabinet_add_document

    def execute(self, context):
        for cabinet in self.get_cabinets():
            cabinet.document_add(document=context['document'])

    def get_cabinets(self):
        return Cabinet.objects.filter(
            pk__in=self.form_data.get('cabinets', ())
        )

    def get_form_schema(self, **kwargs):
        result = super().get_form_schema(**kwargs)

        queryset = AccessControlList.objects.restrict_queryset(
            permission=self.permission, queryset=Cabinet.objects.all(),
            user=kwargs['request'].user
        )

        result['fields']['cabinets']['kwargs']['queryset'] = queryset

        return result


class CabinetRemoveAction(CabinetAddAction):
    fields = {
        'cabinets': {
            'label': _('Cabinet'),
            'class': 'django.forms.ModelMultipleChoiceField', 'kwargs': {
                'help_text': _(
                    'Cabinets from which the document will be removed.'),
                'queryset': Cabinet.objects.none(), 'required': False
            }
        },
    }
    label = _('Remove from cabinets')
    permission = permission_cabinet_remove_document

    def execute(self, context):
        for cabinet in self.get_cabinets():
            cabinet.document_remove(document=context['document'])
