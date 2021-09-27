from django.contrib import admin

from .models import Resume


@admin.register(Resume)
class TagAdmin(admin.ModelAdmin):
    # filter_horizontal = ('documents',)
    list_display = ('first_name', 'last_name', 'applicant_id', 'email', 'phone', 'address', 'reviewer_name', 'comments', 'education', 'work', 'extracurriculars', 'skills_and_awards') # TODO: add new form field names here
