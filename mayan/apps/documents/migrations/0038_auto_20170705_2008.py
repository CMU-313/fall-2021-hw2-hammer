from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0037_auto_20161231_0617'),
    ]

    operations = [
        migrations.AlterField(
            field=models.CharField(
                blank=True, db_index=True, editable=False, max_length=64,
                null=True, verbose_name='Checksum'
            ), model_name='documentversion', name='checksum',
        ),
    ]
