from __future__ import unicode_literals

import yaml

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.serialization import yaml_load

from .models import Transformation


class TransformationForm(forms.ModelForm):
    class Meta:
        fields = ('name', 'arguments', 'order')
        model = Transformation

    def clean(self):
        try:
            yaml_load(stream=self.cleaned_data['arguments'])
        except yaml.YAMLError:
            raise ValidationError(
                _(
                    '"%s" not a valid entry.'
                ) % self.cleaned_data['arguments']
            )
