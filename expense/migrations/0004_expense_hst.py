# Generated by Django 5.1.3 on 2024-12-25 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expense', '0003_expense_receipt2_expense_receipt3_expense_receipt4'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='hst',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
