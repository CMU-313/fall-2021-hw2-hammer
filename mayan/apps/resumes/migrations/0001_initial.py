# Generated by Django 2.2.23 on 2021-09-29 02:29

from django.db import migrations, models
import mayan.apps.databases.model_mixins


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cumulative_Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Resume',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(db_index=True, help_text='', max_length=128, unique=True, verbose_name='Applicant First Name')),
                ('last_name', models.CharField(db_index=True, help_text='', max_length=128, unique=True, verbose_name='Applicant Last Name')),
                ('applicant_id', models.CharField(db_index=True, help_text='', max_length=128, unique=True, verbose_name='Applicant ID')),
                ('reviewer_first_name', models.CharField(db_index=True, help_text='', max_length=128, unique=True, verbose_name='Reviewer First Name')),
                ('reviewer_last_name', models.CharField(db_index=True, help_text='', max_length=128, unique=True, verbose_name='Reviewer Last Name')),
                ('education', models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], help_text="Please take the applicant's GPA, etc. into consideration.", max_length=11)),
                ('work', models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], help_text="Please take the applicant's years of experience and field of expertise into consideration.", max_length=11)),
                ('extracurriculars', models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], help_text="Please take the applicant's hobbies, community service, and other activities into consideration.", max_length=11)),
                ('skills_and_awards', models.CharField(choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')], help_text="Please take the applicant's relevant skills and honors into consideration.", max_length=11)),
                ('comments', models.TextField(db_index=True, help_text='Please comment on this applicant.', unique=True, verbose_name='Reviewer Comments')),
            ],
            bases=(mayan.apps.databases.model_mixins.ExtraDataModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('applicant_first_fame', models.CharField(max_length=30)),
                ('applicant_last_name', models.CharField(max_length=30)),
                ('reviewer_first_name', models.CharField(max_length=30)),
                ('reviewer_last_name', models.CharField(max_length=30)),
                ('applicant_ID', models.CharField(max_length=8, unique=True)),
                ('education_score', models.IntegerField()),
                ('word_score', models.IntegerField()),
                ('extracurriculars_score', models.IntegerField()),
                ('skills_and_award_ccore', models.IntegerField()),
                ('comments', models.CharField(max_length=500)),
            ],
        ),
    ]