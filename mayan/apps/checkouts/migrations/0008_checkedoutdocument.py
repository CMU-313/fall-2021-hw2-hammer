from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0050_auto_20190725_0451'),
        ('checkouts', '0007_auto_20180310_1715'),
    ]

    operations = [
        migrations.CreateModel(
            name='CheckedOutDocument',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('documents.document',),
        ),
    ]
