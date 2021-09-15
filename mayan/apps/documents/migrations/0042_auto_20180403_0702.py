import uuid

import django.core.files.storage
from django.db import migrations, models
from django.utils.encoding import force_text


class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0041_auto_20170823_1855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentversion',
            name='file',
            field=models.FileField(
                storage=django.core.files.storage.FileSystemStorage(
                    location=b'mayan/media/document_storage'
                ), upload_to=force_text(s=uuid.uuid4()), verbose_name='File'
            ),
        ),
    ]
