# Generated by Django 3.2.3 on 2021-05-31 23:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0006_auto_20210531_0933'),
    ]

    operations = [
        migrations.AddField(
            model_name='pesticidalproteinhiddensequence',
            name='toxicto',
            field=models.CharField(blank=True, default='None', max_length=250, null=True),
        ),
    ]