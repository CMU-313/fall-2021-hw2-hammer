from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('document_states', '0006_auto_20170803_0651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workflowinstancelogentry',
            name='user',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL, verbose_name='User'
            ),
        ),
        migrations.AlterField(
            model_name='workflowtransitiontriggerevent',
            name='event_type',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='events.EventType', verbose_name='Event type'
            ),
        ),
        migrations.AlterField(
            model_name='workflowtransitiontriggerevent',
            name='transition',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='trigger_events',
                to='document_states.WorkflowTransition',
                verbose_name='Transition'
            ),
        ),
    ]

    run_before = [
        # In this migration EventType becomes StoredEventType. Therefore this
        # migration needs to run before the source is renamed.
        ('events', '0004_auto_20170731_0423')
    ]
