# Generated by Django 3.1.3 on 2021-08-04 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extra', '0019_auto_20210728_1133'),
    ]

    operations = [
        migrations.CreateModel(
            name='NCBIAvailability',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accession', models.CharField(blank=True, max_length=75, null=True)),
                ('availability', models.CharField(blank=True, max_length=75, null=True)),
            ],
        ),
    ]
