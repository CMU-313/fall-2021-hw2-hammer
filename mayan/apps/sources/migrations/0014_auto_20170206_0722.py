from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('sources', '0013_auto_20170206_0710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sanescanner',
            name='adf_mode',
            field=models.CharField(
                blank=True, choices=[
                    ('simplex', 'Simplex'), ('duplex', 'Duplex')
                ], default='simplex', help_text='Selects the document feeder '
                'mode (simplex/duplex). If this option is not supported by '
                'your scanner, leave it blank.', max_length=16,
                verbose_name='ADF mode'
            ),
        ),
        migrations.AlterField(
            model_name='sanescanner',
            name='source',
            field=models.CharField(
                blank=True, choices=[
                    ('flatbed', 'Flatbed'),
                    ('"Automatic Document Feeder"', 'Document feeder')
                ], default='flatbed', help_text='Selects the scan source '
                '(such as a document-feeder). If this option is not '
                'supported by your scanner, leave it blank.', max_length=32,
                verbose_name='Paper source'
            ),
        ),
    ]
