from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('document_states', '0016_auto_20191108_2332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workflow', name='label', field=models.CharField(
                help_text='A short text to describe the workflow.',
                max_length=255, unique=True, verbose_name='Label'
            ),
        ),
        migrations.AlterField(
            model_name='workflowstate', name='label', field=models.CharField(
                help_text='A short text to describe the workflow state.',
                max_length=255, verbose_name='Label'
            ),
        ),
        migrations.AlterField(
            model_name='workflowstateaction', name='label',
            field=models.CharField(
                help_text='A short text describing the action.',
                max_length=255, verbose_name='Label'
            ),
        ),
        migrations.AlterField(
            model_name='workflowtransition', name='label',
            field=models.CharField(
                help_text='A short text to describe the transition.',
                max_length=255, verbose_name='Label'
            ),
        ),
    ]
