from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('linking', '0006_auto_20180402_0339'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smartlink',
            name='dynamic_label',
            field=models.CharField(
                blank=True, help_text="Enter a template to render. Use "
                "Django's default templating language "
                "(https://docs.djangoproject.com/en/1.11/ref/templates/builtins/). "
                "The {{ document }} context variable is available.",
                max_length=96, verbose_name='Dynamic label'
            ),
        ),
        migrations.AlterField(
            model_name='smartlinkcondition',
            name='expression',
            field=models.TextField(
                help_text="Enter a template to render. Use Django's default "
                "templating language "
                "(https://docs.djangoproject.com/en/1.11/ref/templates/builtins/). "
                "The {{ document }} context variable is available.",
                verbose_name='Expression'
            ),
        ),
    ]
