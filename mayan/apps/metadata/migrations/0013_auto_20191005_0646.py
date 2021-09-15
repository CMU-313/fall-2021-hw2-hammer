from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('metadata', '0012_auto_20190612_0526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metadatatype',
            name='label',
            field=models.CharField(
                help_text='Short description of this metadata type.',
                max_length=48, verbose_name='Label'
            ),
        ),
    ]
