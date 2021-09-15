from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('document_indexing', '0016_auto_20191005_0647'),
    ]

    operations = [
        migrations.AlterField(
            model_name='indexinstancenode',
            name='level',
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='indexinstancenode',
            name='lft',
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='indexinstancenode',
            name='rght',
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='indextemplatenode',
            name='level',
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='indextemplatenode',
            name='lft',
            field=models.PositiveIntegerField(editable=False),
        ),
        migrations.AlterField(
            model_name='indextemplatenode',
            name='rght',
            field=models.PositiveIntegerField(editable=False),
        ),
    ]
