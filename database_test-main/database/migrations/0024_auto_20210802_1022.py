# Generated by Django 3.1.3 on 2021-08-02 15:22

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0023_auto_20210802_1020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pesticidalproteindatabase',
            name='taxonid',
            field=models.CharField(blank=True, max_length=25, null=True, validators=[django.core.validators.RegexValidator(message='digits allowed.', regex='\\d{1,25}$')]),
        ),
    ]
