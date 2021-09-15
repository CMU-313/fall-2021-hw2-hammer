from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('metadata', '0010_auto_20180823_2353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentmetadata',
            name='value',
            field=models.CharField(
                blank=True, db_index=True,
                help_text='The actual value stored in the metadata type '
                'field for the document.', max_length=255, null=True,
                verbose_name='Value'
            ),
        ),
        migrations.AlterField(
            model_name='metadatatype',
            name='name',
            field=models.CharField(
                help_text='Name used by other apps to reference this '
                'metadata type. Do not use python reserved words, or spaces.',
                max_length=48, unique=True, verbose_name='Name'
            ),
        ),
    ]
