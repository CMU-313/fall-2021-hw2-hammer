import datetime

from django import forms
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.literals import TIME_DELTA_UNIT_CHOICES
from mayan.apps.views.widgets import NamedMultiWidget


class SplitTimeDeltaWidget(NamedMultiWidget):
    """
    A Widget that splits a timedelta input into two field: one for unit of
    time and another for the amount of units.
    """
    subwidgets = {
        'unit': forms.widgets.Select(
            attrs={'style': 'width: 8em;'}, choices=TIME_DELTA_UNIT_CHOICES
        ),
        'amount': forms.widgets.NumberInput(
            attrs={
                'maxlength': 4, 'style': 'width: 8em;',
                'placeholder': _('Amount')
            }
        )
    }

    def decompress(self, value):
        return {
            'unit': None, 'amount': None
        }

    def value_from_datadict(self, querydict, files, name):
        unit = querydict.get('{}_unit'.format(name))
        amount = querydict.get('{}_amount'.format(name))

        if not unit or not amount:
            return now()

        amount = int(amount)

        timedelta = datetime.timedelta(**{unit: amount})
        return now() + timedelta
