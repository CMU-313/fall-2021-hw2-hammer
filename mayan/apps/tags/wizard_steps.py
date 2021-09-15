from django.apps import apps
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from mayan.apps.sources.classes import DocumentCreateWizardStep
from mayan.apps.views.http import URL

from .forms import TagMultipleSelectionForm
from .models import Tag
from .permissions import permission_tag_attach


class DocumentCreateWizardStepTags(DocumentCreateWizardStep):
    form_class = TagMultipleSelectionForm
    label = _('Select tags')
    name = 'tag_selection'
    number = 2

    @classmethod
    def condition(cls, wizard):
        Tag = apps.get_model(app_label='tags', model_name='Tag')
        return Tag.objects.exists()

    @classmethod
    def get_form_kwargs(self, wizard):
        return {
            'help_text': _('Tags to be attached.'),
            'model': Tag,
            'permission': permission_tag_attach,
            'user': wizard.request.user
        }

    @classmethod
    def done(cls, wizard):
        result = {}
        cleaned_data = wizard.get_cleaned_data_for_step(cls.name)
        if cleaned_data:
            result['tags'] = [
                force_text(s=tag.pk) for tag in cleaned_data['tags']
            ]

        return result

    @classmethod
    def step_post_upload_process(cls, document, querystring=None):
        Tag = apps.get_model(app_label='tags', model_name='Tag')

        tag_id_list = URL(query_string=querystring).args.getlist('tags')

        for tag in Tag.objects.filter(pk__in=tag_id_list):
            tag.documents.add(document)


DocumentCreateWizardStep.register(step=DocumentCreateWizardStepTags)
