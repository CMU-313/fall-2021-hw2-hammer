from django import forms
from django.utils.encoding import force_text
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, ugettext

from mayan.apps.views.widgets import TextAreaDiv

from .models import DocumentFilePageContent


class DocumentFileContentForm(forms.Form):
    """
    Form that concatenates all of a document pages' text content into a
    single textarea widget
    """
    def __init__(self, *args, **kwargs):
        self.document = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        content = []
        self.fields['contents'].initial = ''
        try:
            document_pages = self.document.pages.all()
        except AttributeError:
            document_pages = []

        for page in document_pages:
            try:
                page_content = page.content.content
            except DocumentFilePageContent.DoesNotExist:
                pass
            else:
                content.append(conditional_escape(force_text(s=page_content)))
                content.append(
                    '\n\n\n<hr/><div class="document-page-content-divider">- %s -</div><hr/>\n\n\n' % (
                        ugettext(
                            'Page %(page_number)d'
                        ) % {'page_number': page.page_number}
                    )
                )

        self.fields['contents'].initial = mark_safe(''.join(content))

    contents = forms.CharField(
        label=_('Contents'),
        widget=TextAreaDiv(
            attrs={
                'class': 'text_area_div full-height',
                'data-height-difference': 360
            }
        )
    )


class DocumentFilePageContentForm(forms.Form):
    contents = forms.CharField(
        label=_('Contents'),
        widget=TextAreaDiv(
            attrs={
                'class': 'text_area_div full-height',
                'data-height-difference': 360
            }
        )
    )

    def __init__(self, *args, **kwargs):
        document_page = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        content = ''
        self.fields['contents'].initial = ''

        try:
            page_content = document_page.content.content
        except DocumentFilePageContent.DoesNotExist:
            pass
        else:
            content = conditional_escape(force_text(s=page_content))

        self.fields['contents'].initial = mark_safe(content)
