import yaml

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.serialization import yaml_load


@deconstructible
class YAMLValidator:
    """
    Validates that the input is YAML compliant.
    """
    def __call__(self, value):
        value = value.strip()
        try:
            yaml_load(stream=value)
        except yaml.error.YAMLError:
            raise ValidationError(
                _('Enter a valid YAML value.'),
                code='invalid'
            )

    def __eq__(self, other):
        return (
            isinstance(other, YAMLValidator)
        )

    def __ne__(self, other):
        return not (self == other)
