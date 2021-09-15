from django.db import migrations, models
import mayan.apps.common.validators


class Migration(migrations.Migration):
    dependencies = [
        ('document_states', '0014_auto_20190701_0454'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflowtransitionfield',
            name='widget',
            field=models.PositiveIntegerField(
                blank=True, choices=[(1, 'Text area')],
                help_text='An optional class to change the default '
                'presentation of the field.', null=True,
                verbose_name='Widget class'
            ),
        ),
        migrations.AddField(
            model_name='workflowtransitionfield',
            name='widget_kwargs',
            field=models.TextField(
                blank=True,
                help_text='A group of keyword arguments to customize the '
                'widget. Use YAML format.', validators=[
                    mayan.apps.common.validators.YAMLValidator()
                ], verbose_name='Widget keyword arguments'
            ),
        ),
        migrations.AlterField(
            model_name='workflowinstance',
            name='context',
            field=models.TextField(blank=True, verbose_name='Context'),
        ),
    ]
