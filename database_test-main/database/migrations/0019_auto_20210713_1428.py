# Generated by Django 3.1.3 on 2021-07-13 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0018_auto_20210713_1333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pesticidalproteinprivatedatabase',
            name='accession',
            field=models.CharField(blank=True, max_length=25, null=True, verbose_name='NCBI accession number'),
        ),
        migrations.AlterField(
            model_name='pesticidalproteinprivatedatabase',
            name='year',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]
