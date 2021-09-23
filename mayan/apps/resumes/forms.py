from django.utils.translation import ugettext_lazy as _

from mayan.apps.views.forms import FilteredSelectionForm
from django.forms.widgets import RadioSelect
from .widgets import TagFormWidget
from django import forms
from mayan.apps.resumes.models import Resume


class TagMultipleSelectionForm(FilteredSelectionForm):
    class Media:
        js = ('tags/js/tags_form.js',)

    class Meta:
        allow_multiple = True
        field_name = 'tags'
        label = _('Tags')
        required = False
        widget_class = TagFormWidget
        widget_attributes = {'class': 'select2-tags'}

class ResumeForm(forms.ModelForm):

    class Meta:
           model = Resume
           fields = '__all__'
           widgets = {
               'education': RadioSelect(),
               'work': RadioSelect(),
               'extracurriculars': RadioSelect(),
               'skills_and_awards': RadioSelect(),
           }  
