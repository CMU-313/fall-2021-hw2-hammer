from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('permissions', '0003_remove_role_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='label',
            field=models.CharField(
                help_text='A short text describing the role.',
                max_length=128, unique=True, verbose_name='Label'
            ),
        ),
    ]
