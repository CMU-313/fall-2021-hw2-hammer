# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pycountry

from django.db import migrations


def change_bibliographic_to_terminology(apps, schema_editor):
    Document = apps.get_model('documents', 'Document')

    for document in Document.objects.all():
        language = pycountry.languages.get(bibliographic=document.language)
        document.language = language.terminology
        document.save()


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0024_auto_20150715_0714'),
    ]

    operations = [
        migrations.RunPython(change_bibliographic_to_terminology),
    ]
