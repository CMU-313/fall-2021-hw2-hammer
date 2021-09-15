from django.db import models, migrations

import mayan.apps.common.validators


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transformation',
            fields=[
                (
                    'id', models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True,
                        primary_key=True
                    )
                ),
                ('object_id', models.PositiveIntegerField()),
                (
                    'order', models.PositiveIntegerField(
                        default=0, null=True, verbose_name='Order',
                        db_index=True, blank=True
                    )
                ),
                (
                    'transformation', models.CharField(
                        max_length=128, verbose_name='Transformation',
                        choices=[
                            ('rotate', 'Rotate'), ('zoom', 'Zoom'),
                            ('resize', 'Resize')
                        ]
                    )
                ),
                (
                    'arguments', models.TextField(
                        blank=True, null=True, verbose_name='Arguments',
                        validators=[
                            mayan.apps.common.validators.YAMLValidator
                        ]
                    )
                ),
                (
                    'content_type',
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        to='contenttypes.ContentType'
                    )
                ),
            ],
            options={
                'ordering': ('order',),
                'verbose_name': 'Transformation',
                'verbose_name_plural': 'Transformations',
            },
            bases=(models.Model,),
        ),
    ]
