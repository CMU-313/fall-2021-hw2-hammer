from django.contrib import admin

from .models import Review


@admin.register(Review)
class TagAdmin(admin.ModelAdmin):
    # filter_horizontal = ('documents',)
    list_display = ('applicant_id', 'reviewer_first_name', 'reviewer_last_name', 'education', 'work', 'extracurriculars', 'skills_and_awards', 'comments') # TODO: add new form field names here

