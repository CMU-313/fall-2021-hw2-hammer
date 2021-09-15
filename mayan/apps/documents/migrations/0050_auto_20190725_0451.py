from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0049_auto_20190715_0454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='language',
            field=models.CharField(
                blank=True, default='eng',
                help_text='The dominant language in the document.',
                max_length=8, verbose_name='Language'
            ),
        ),
    ]
