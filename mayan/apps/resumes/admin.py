from django.contrib import admin

from .models import Resume


@admin.register(Resume)
class TagAdmin(admin.ModelAdmin):
    # filter_horizontal = ('documents',)
    list_display = ('label', 'color')
