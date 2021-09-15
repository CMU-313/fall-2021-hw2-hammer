import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('file_caching', '0003_auto_20191130_2208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cache',
            name='maximum_size',
            field=models.BigIntegerField(
                help_text='Maximum size of the cache in bytes.',
                validators=[
                    django.core.validators.MinValueValidator(limit_value=1)
                ], verbose_name='Maximum size'
            ),
        ),
    ]
