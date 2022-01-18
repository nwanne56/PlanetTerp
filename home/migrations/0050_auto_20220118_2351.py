# Generated by Django 3.2.4 on 2022-01-18 23:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0049_course_unique_course_name'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='grade',
            index=models.Index(fields=['semester'], name='home_grade_semeste_7037cd_idx'),
        ),
        migrations.AddIndex(
            model_name='grade',
            index=models.Index(fields=['section'], name='home_grade_section_6e3ca4_idx'),
        ),
    ]
