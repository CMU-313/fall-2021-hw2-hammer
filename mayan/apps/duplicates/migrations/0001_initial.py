from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('documents', '0074_auto_20201130_0341'),
    ]

    operations = [
        migrations.CreateModel(
            name='DuplicatedDocument',
            fields=[
                (
                    'id', models.AutoField(
                        auto_created=True, primary_key=True, serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'datetime_added', models.DateTimeField(
                        auto_now_add=True, db_index=True, verbose_name='Added'
                    )
                ),
                (
                    'document', models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='duplicates', to='documents.Document',
                        verbose_name='Document'
                    )
                ),
                (
                    'documents', models.ManyToManyField(
                        to='documents.Document',
                        verbose_name='Duplicated documents'
                    )
                ),
            ],
            options={
                'verbose_name': 'Duplicated document',
                'verbose_name_plural': 'Duplicated documents',
            },
        ),
    ]
