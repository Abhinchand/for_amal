# Generated by Django 3.2.3 on 2021-05-31 14:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('extra', '0004_auto_20210510_1326'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='links',
            options={'ordering': ('name',), 'verbose_name': 'Add External Link', 'verbose_name_plural': 'Add External Links'},
        ),
    ]