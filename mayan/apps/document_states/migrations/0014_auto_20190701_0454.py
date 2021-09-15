from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('document_states', '0013_auto_20190423_0810'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkflowTransitionField',
            fields=[
                (
                    'id', models.AutoField(
                        auto_created=True, primary_key=True, serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'field_type', models.PositiveIntegerField(
                        choices=[(1, 'Character'), (2, 'Number (Integer)')],
                        verbose_name='Type'
                    )
                ),
                (
                    'name', models.CharField(
                        help_text='The name that will be used to identify '
                        'this field in other parts of the workflow system.',
                        max_length=128, verbose_name='Internal name'
                    )
                ),
                (
                    'label', models.CharField(
                        help_text='The field name that will be shown on '
                        'the user interface.', max_length=128,
                        verbose_name='Label'
                    )
                ),
                (
                    'help_text', models.TextField(
                        blank=True, help_text='An optional message that '
                        'will help users better understand the purpose '
                        'of the field and data to provide.',
                        verbose_name='Help text'
                    )
                ),
                (
                    'required', models.BooleanField(
                        default=False, help_text='Whether this fields '
                        'needs to be filled out or not to proceed.',
                        verbose_name='Required'
                    )
                ),
                (
                    'transition', models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='fields',
                        to='document_states.WorkflowTransition',
                        verbose_name='Transition'
                    )
                ),
            ],
            options={
                'verbose_name': 'Workflow transition trigger event',
                'verbose_name_plural': 'Workflow transitions trigger events',
            },
        ),
        migrations.AddField(
            model_name='workflowinstance',
            name='context',
            field=models.TextField(blank=True, verbose_name='Backend data'),
        ),
        migrations.AddField(
            model_name='workflowinstancelogentry',
            name='extra_data',
            field=models.TextField(blank=True, verbose_name='Extra data'),
        ),
        migrations.AlterUniqueTogether(
            name='workflowtransitionfield',
            unique_together=set([('transition', 'name')]),
        ),
    ]
