from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0034_auto_20160509_2321'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentPageCachedImage',
            fields=[
                (
                    'id', models.AutoField(
                        auto_created=True, primary_key=True, serialize=False,
                        verbose_name='ID'
                    )
                ),
                (
                    'filename', models.CharField(
                        max_length=128, verbose_name='Filename'
                    )
                ),
            ],
            options={
                'verbose_name': 'Document page cached image',
                'verbose_name_plural': 'Document page cached images',
            },
        ),
        migrations.CreateModel(
            name='DocumentPageResult',
            fields=[
            ],
            options={
                'ordering': ('document_version__document', 'page_number'),
                'verbose_name': 'Document page',
                'proxy': True,
                'verbose_name_plural': 'Document pages',
            },
            bases=('documents.documentpage',),
        ),
        migrations.AddField(
            model_name='documentpagecachedimage',
            name='document_page',
            field=models.ForeignKey(
                on_delete=models.CASCADE, related_name='cached_images',
                to='documents.DocumentPage', verbose_name='Document page'
            ),
        ),
    ]
