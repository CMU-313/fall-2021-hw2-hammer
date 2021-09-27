# from typing_extensions import Required
from django.db import models
from django import forms
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _


# from mayan.apps.acls.models import AccessControlList
from mayan.apps.databases.model_mixins import ExtraDataModelMixin
# from mayan.apps.events.classes import EventManagerMethodAfter, EventManagerSave
# from mayan.apps.events.decorators import method_event
# from mayan.apps.documents.models import Document
# from mayan.apps.documents.permissions import permission_document_view

# from .events import (
#     event_tag_attached, event_tag_created, event_tag_edited, event_tag_removed
# )
# from .html_widgets import widget_single_tag


class Resume(ExtraDataModelMixin, models.Model):
    """
    This model represents a form to upload resumes.
    """

    """
    NEW FIELD CREATION PROCESS:
    1. Follow one of the two templates provided below.
    2. Add the field name to the 'fields' and 'list_display' variables:
        - 'fields' is located in the 'ResumeCreateView' class defined in 'views.py'
        - 'list_display' is located in the 'TagAdmin' class defined in 'admin.py'
    """

    """
    Text Input Field Template:

    FIELD_NAME = models.CharField(
        db_index=True, help_text=_(
            ''
        ), max_length=CHAR_LENGTH, unique=True, verbose_name=_('FIELD_DESCRIPTION'), blank=REQUIRED
    )

    FIELD_NAME: Name of the field
    CHAR_LENGTH: The maximum character length of an input for this field
    FIELD_DESCRIPTION: What the end user sees as the name of the form
    REQUIRED: A boolean that represents whether or not this field is required to submit the form
              True -> field is required, False -> field is not required
    """
    """
    Radio Input Field Template:

    choiceArray = [('CHOICE_INTERNAL_1', 'CHOICE_EXTERNAL_1'), ('CHOICE_INTERNAL_2', 'CHOICE_EXTERNAL_2'), ...]
    FIELD_NAME = models.CharField(max_length=CHAR_LENGTH, choices=choiceArray, help_text="FIELD_DESCRIPTION"

    choiceArray: An array of tuples, where each tuple represents a single field option
    CHOICE_INTERNAL_N: The internal (developer-facing) name of the field option
    CHOICE_EXTERNAL_N: The external (customer-facing) name of the field option; for our purposes it should be
                       fine to have CHOICE_INTERNAL_N and CHOICE_EXTERNAL_N to be identical to each other
    FIELD_NAME: The name of the field
    CHAR_LENGTH: The maximum character length of an input for this field
    FIELD_DESCRIPTION: A brief description or help text that will be displayed under the field
    """
    first_name = models.CharField(
        db_index=True, help_text=_(
            ''
        ), max_length=128, unique=True, verbose_name=_('Applicant First Name')
    )

    last_name = models.CharField(
        db_index=True, help_text=_(
            ''
        ), max_length=128, unique=True, verbose_name=_('Applicant Last Name')
    )

    applicant_id = models.CharField(
        db_index=True, help_text=_(
            ''
        ), max_length=128, unique=True, verbose_name=_('Applicant ID')
    )

    email = models.CharField(
        db_index=True, help_text=_(
            ''
        ), max_length=128, unique=True, verbose_name=_('Applicant Email'), blank=True
    )

    phone = models.CharField(
        db_index=True, help_text=_(
            ''
        ), max_length=128, unique=True, verbose_name=_('Applicant Phone Number'), blank=True
    )

    address = models.CharField(
        db_index=True, help_text=_(
            ''
        ), max_length=128, unique=True, verbose_name=_('Applicant Home Address'), blank=True
    )

    reviewer_name = models.CharField(
        db_index=True, help_text=_(
            ''
        ), max_length=128, unique=True, verbose_name=_('Reviewer Name')
    )

    comments = models.TextField(
        db_index=True, help_text=_(
            ''
        ), unique=True, verbose_name=_('Reviewer Comments')
    )

    CHOICES = [('1','1'),('2','2'),('3','3'),('4','4'),('5','5')]
    education = models.CharField(max_length=11, choices=CHOICES, help_text="Please take the applicant's GPA, etc. into consideration.")

    work = models.CharField(max_length=11, choices=CHOICES, help_text="Please take the applicant's years of experience and field of expertise into consideration.")
    extracurriculars = models.CharField(max_length=11, choices=CHOICES, help_text="Please take the applicant's hobbies, community service, and other activities into consideration.")
    skills_and_awards = models.CharField(max_length=11, choices=CHOICES, help_text="Please take the applicant's relevant skills and honors into consideration.")

    # TODO: add more form fields


    # class Meta:
    #     ordering = ('label',)
    #     verbose_name = _('Tag')
    #     verbose_name_plural = _('Tags')

    def __str__(self):
        return self.name

    # @method_event(
    #     action_object='self',
    #     event=event_tag_attached,
    #     event_manager_class=EventManagerMethodAfter,
    # )
    # def attach_to(self, document):
    #     self._event_target = document
    #     self.documents.add(document)

    # def get_absolute_url(self):
    #     return reverse(
    #         viewname='tags:tag_document_list', kwargs={'tag_id': self.pk}
    #     )

    # def get_document_count(self, user):
    #     """
    #     Return the numeric count of documents that have this tag attached.
    #     The count is filtered by access.
    #     """
    #     return self.get_documents(permission=permission_document_view, user=user).count()

    # def get_documents(self, user, permission=None):
    #     """
    #     Return a filtered queryset documents that have this tag attached.
    #     """
    #     queryset = self.documents.all()

    #     if permission:
    #         queryset = AccessControlList.objects.restrict_queryset(
    #             permission=permission_document_view, queryset=queryset,
    #             user=user
    #         )

    #     return queryset

    # def get_preview_widget(self):
    #     return widget_single_tag(tag=self)
    # get_preview_widget.short_description = _('Preview')

    # @method_event(
    #     action_object='self',
    #     event=event_tag_removed,
    #     event_manager_class=EventManagerMethodAfter,
    # )
    # def remove_from(self, document):
    #     self._event_target = document
    #     self.documents.remove(document)

    # @method_event(
    #     event_manager_class=EventManagerSave,
    #     created={
    #         'event': event_tag_created,
    #         'target': 'self',
    #     },
    #     edited={
    #         'event': event_tag_edited,
    #         'target': 'self',
    #     }
    # )
    # def save(self, *args, **kwargs):
    #     return super().save(*args, **kwargs)


# class DocumentTag(Tag):
#     class Meta:
#         proxy = True
#         verbose_name = _('Document tag')
#         verbose_name_plural = _('Document tags')
