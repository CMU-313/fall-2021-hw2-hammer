from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('converter', '0012_auto_20170714_2133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transformation',
            name='name',
            field=models.CharField(
                choices=[
                    ('crop', 'Crop: left, top, right, bottom'),
                    ('flip', 'Flip'),
                    ('gaussianblur', 'Gaussian blur: radius'),
                    ('lineart', 'Line art'), ('mirror', 'Mirror'),
                    ('resize', 'Resize: width, height'),
                    ('rotate', 'Rotate: degrees, fillcolor'),
                    ('rotate180', 'Rotate 180 degrees'),
                    ('rotate270', 'Rotate 270 degrees'),
                    ('rotate90', 'Rotate 90 degrees'),
                    (
                        'unsharpmask',
                        'Unsharp masking: radius, percent, threshold'
                    ), ('zoom', 'Zoom: percent')
                ], max_length=128, verbose_name='Name'
            ),
        ),
    ]
