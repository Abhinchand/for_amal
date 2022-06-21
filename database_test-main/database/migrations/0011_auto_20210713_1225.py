# Generated by Django 3.1.3 on 2021-07-13 17:25

import database.storage
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0010_auto_20210713_0957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pesticidalproteindatabase',
            name='fastasequence_file',
            field=models.FileField(blank=True, null=True, storage=database.storage.OverwriteStorage(), upload_to='fastasequence_files/'),
        ),
        migrations.AlterField(
            model_name='pesticidalproteinhiddensequence',
            name='taxonid',
            field=models.CharField(blank=True, max_length=25, null=True, validators=[django.core.validators.RegexValidator('\\d{2,9}', 'Number must digits', 'Invalid number')]),
        ),
    ]
