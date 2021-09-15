from django.db import migrations, models


def operation_remove_duplicates(apps, schema_editor):
    StoredDriver = apps.get_model(
        app_label='file_metadata', model_name='StoredDriver'
    )
    DocumentVersionDriverEntry = apps.get_model(
        app_label='file_metadata', model_name='DocumentVersionDriverEntry'
    )

    driver = StoredDriver.objects.first()
    if driver:
        DocumentVersionDriverEntry.objects.using(alias=schema_editor.connection.alias).update(driver=driver)

        StoredDriver.objects.exclude(pk=driver.id).delete()


class Migration(migrations.Migration):
    atomic = False
    dependencies = [
        ('file_metadata', '0002_documenttypesettings'),
    ]
    operations = [
        migrations.RunPython(
            code=operation_remove_duplicates,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='storeddriver',
            name='driver_path',
            field=models.CharField(
                max_length=255, unique=True, verbose_name='Driver path'
            ),
        ),
        migrations.AlterField(
            model_name='storeddriver',
            name='internal_name',
            field=models.CharField(
                db_index=True, max_length=128, unique=True,
                verbose_name='Internal name'
            ),
        ),
    ]
    run_before = [
        ('documents', '0057_auto_20200916_1057'),
    ]
