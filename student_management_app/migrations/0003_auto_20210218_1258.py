# Generated by Django 3.1.5 on 2021-02-18 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student_management_app', '0002_auto_20210214_1834'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='attendance_date',
            field=models.DateField(),
        ),
    ]