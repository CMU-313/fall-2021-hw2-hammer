from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def operation_create_setting_for_existing_document_types(apps, schema_editor):
    DocumentType = apps.get_model(
        app_label='documents', model_name='DocumentType'
    )
    DocumentTypeSettings = apps.get_model(
        app_label='file_metadata', model_name='DocumentTypeSettings'
    )

    for document_type in DocumentType.objects.using(schema_editor.connection.alias).all():
        DocumentTypeSettings.objects.using(
            schema_editor.connection.alias
        ).create(document_type=document_type)


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('documents', '0049_auto_20181211_0011'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentTypeSettings',
            fields=[
                (
                    'id', models.AutoField(
                        auto_created=True, primary_key=True, serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'auto_process', models.BooleanField(
                        default=True, verbose_name='Automatically queue '
                        'newly created documents for processing.'
                    )
                ),
                (
                    'document_type', models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='file_metadata_settings',
                        to='documents.DocumentType',
                        verbose_name='Document type'
                    )
                ),
            ],
            options={
                'verbose_name': 'Document type settings',
                'verbose_name_plural': 'Document types settings',
            },
        ),
        migrations.CreateModel(
            name='DocumentVersionDriverEntry',
            fields=[
                (
                    'id', models.AutoField(
                        auto_created=True, primary_key=True, serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'document_version', models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='file_metadata_drivers',
                        to='documents.DocumentVersion',
                        verbose_name='Document version'
                    )
                ),
            ],
            options={
                'ordering': ('document_version', 'driver'),
                'verbose_name': 'Document version driver entry',
                'verbose_name_plural': 'Document version driver entries',
            },
        ),
        migrations.CreateModel(
            name='FileMetadataEntry',
            fields=[
                (
                    'id', models.AutoField(
                        auto_created=True, primary_key=True, serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'key', models.CharField(
                        db_index=True, max_length=255, verbose_name='Key'
                    )
                ),
                (
                    'value', models.CharField(
                        db_index=True, max_length=255, verbose_name='Value'
                    )
                ),
                (
                    'document_version_driver_entry', models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='entries',
                        to='file_metadata.DocumentVersionDriverEntry',
                        verbose_name='Document version driver entry'
                    )
                ),
            ],
            options={
                'ordering': ('key', 'value'),
                'verbose_name': 'File metadata entry',
                'verbose_name_plural': 'File metadata entries',
            },
        ),
        migrations.CreateModel(
            name='StoredDriver',
            fields=[
                (
                    'id', models.AutoField(
                        auto_created=True, primary_key=True, serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'driver_path', models.CharField(
                        max_length=255, verbose_name='Driver path'
                    )
                ),
                (
                    'internal_name', models.CharField(
                        db_index=True, max_length=128,
                        verbose_name='Internal name'
                    )
                ),
            ],
            options={
                'ordering': ('internal_name',),
                'verbose_name': 'Driver',
                'verbose_name_plural': 'Drivers',
            },
        ),
        migrations.AddField(
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='driver_entries', to='file_metadata.StoredDriver',
                verbose_name='Driver'
            ),
            model_name='documentversiondriverentry',
            name='driver'
        ),
        migrations.AlterUniqueTogether(
            name='documentversiondriverentry',
            unique_together=set([('driver', 'document_version')]),
        ),
        migrations.RunPython(
            code=operation_create_setting_for_existing_document_types
        ),
    ]
