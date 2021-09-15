from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('sources', '0017_auto_20180510_2151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sanescanner',
            name='adf_mode',
            field=models.CharField(
                blank=True, choices=[
                    ('simplex', 'Simplex'), ('duplex', 'Duplex')
                ],
                help_text='Selects the document feeder mode '
                '(simplex/duplex). If this option is not supported by your '
                'scanner, leave it blank.', max_length=16,
                verbose_name='ADF mode'
            ),
        ),
    ]
