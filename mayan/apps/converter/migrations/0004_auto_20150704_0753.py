from django.db import models, migrations

import mayan.apps.converter.validators


class Migration(migrations.Migration):
    dependencies = [
        ('converter', '0003_auto_20150704_0731'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transformation',
            name='arguments',
            field=models.TextField(
                help_text='Enter the arguments for the transformation as a '
                'YAML dictionary. ie: {"degrees": 180}',
                blank=True, verbose_name='Arguments',
                validators=[mayan.apps.converter.validators.YAMLValidator()]
            ),
            preserve_default=True,
        ),
    ]
