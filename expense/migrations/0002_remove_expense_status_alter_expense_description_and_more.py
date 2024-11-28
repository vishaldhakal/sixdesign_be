# Generated by Django 5.1.3 on 2024-11-28 04:16

import django.utils.timezone
import tinymce.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expense', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='expense',
            name='status',
        ),
        migrations.AlterField(
            model_name='expense',
            name='description',
            field=tinymce.models.HTMLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='expense',
            name='expense_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
