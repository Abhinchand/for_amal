# Generated by Django 3.2 on 2022-01-21 22:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('association', '0019_auto_20211105_1249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='association',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='feedbackproteinerror',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='identicalproteins',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='mutantproteindatabase',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
