import datetime

from django.db import models, migrations
from django.utils.timezone import utc


class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0009_document_in_trash'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeletedDocument',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('documents.document',),
        ),
        migrations.AddField(
            model_name='document',
            name='deleted_date_time',
            field=models.DateTimeField(
                default=datetime.datetime(
                    2015, 7, 4, 0, 54, 7, 910642, tzinfo=utc
                ), verbose_name='Date and time deleted', blank=True
            ),
            preserve_default=False,
        ),
    ]
