from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ('checkouts', '0003_auto_20150617_0325'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documentcheckout',
            name='user_content_type',
        ),
        migrations.RemoveField(
            model_name='documentcheckout',
            name='user_object_id',
        ),
        migrations.AlterField(
            model_name='documentcheckout',
            name='user',
            field=models.ForeignKey(
                on_delete=models.CASCADE, to=settings.AUTH_USER_MODEL,
                verbose_name='User'
            ),
            preserve_default=True,
        ),
    ]
