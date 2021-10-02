from django.utils.translation import ugettext_lazy as _

from mayan.apps.views.forms import FilteredSelectionForm
from django.forms.widgets import RadioSelect
from .widgets import TagFormWidget
from django import forms
from mayan.apps.reviews.models import Review


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

class ReviewForm(forms.ModelForm):

    class Meta:
           model = Review
           fields = '__all__'
           widgets = {
               'education': RadioSelect(),
               'work': RadioSelect(),
               'extracurriculars': RadioSelect(),
               'skills_and_awards': RadioSelect(),
           }  
