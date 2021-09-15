from django.db import models, migrations

import mayan.apps.converter.models


class Migration(migrations.Migration):
    dependencies = [
        ('converter', '0005_auto_20150708_0118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transformation',
            name='arguments',
            field=models.TextField(
                help_text='Enter the arguments for the transformation as a '
                'YAML dictionary. ie: {"degrees": 180}', blank=True,
                verbose_name='Arguments', validators=getattr(
                    mayan.apps.converter.models, 'validators', []
                )
            ),
            preserve_default=True,
        ),
    ]
