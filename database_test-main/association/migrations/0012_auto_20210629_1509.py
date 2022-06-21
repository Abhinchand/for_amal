# Generated by Django 3.1.3 on 2021-06-29 20:09

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('association', '0011_identicalproteins'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='identicalproteins',
            name='protein1',
        ),
        migrations.RemoveField(
            model_name='identicalproteins',
            name='protein2',
        ),
        migrations.AddField(
            model_name='identicalproteins',
            name='proteins',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=10000, null=True), default=list, size=None),
        ),
    ]