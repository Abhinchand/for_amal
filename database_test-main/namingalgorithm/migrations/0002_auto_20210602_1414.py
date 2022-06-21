# Generated by Django 3.1.3 on 2021-06-02 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('namingalgorithm', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='archive',
            name='contact_status',
            field=models.CharField(choices=[('emailed', 'Emailed'), ('pending', 'Pending')], default='emailed', max_length=10),
        ),
        migrations.AddField(
            model_name='usersubmission',
            name='contact_status',
            field=models.CharField(choices=[('emailed', 'Emailed'), ('pending', 'Pending')], default='emailed', max_length=10),
        ),
    ]
