from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

FIELD_TYPE_CHOICE_CHAR = 1
FIELD_TYPE_CHOICE_INTEGER = 2
FIELD_TYPE_CHOICES = (
    (FIELD_TYPE_CHOICE_CHAR, _('Character')),
    (FIELD_TYPE_CHOICE_INTEGER, _('Number (Integer)')),
)

FIELD_TYPE_MAPPING = {
    FIELD_TYPE_CHOICE_CHAR: 'django.forms.CharField',
    FIELD_TYPE_CHOICE_INTEGER: 'django.forms.IntegerField',
}

WIDGET_CLASS_TEXTAREA = 1
WIDGET_CLASS_CHOICES = (
    (WIDGET_CLASS_TEXTAREA, _('Text area')),
)

WIDGET_CLASS_MAPPING = {
    WIDGET_CLASS_TEXTAREA: 'django.forms.widgets.Textarea',
}

WORKFLOW_ACTION_ON_ENTRY = 1
WORKFLOW_ACTION_ON_EXIT = 2

WORKFLOW_ACTION_WHEN_CHOICES = (
    (WORKFLOW_ACTION_ON_ENTRY, _('On entry')),
    (WORKFLOW_ACTION_ON_EXIT, _('On exit')),
)
