# Generated by Django 3.1.3 on 2021-06-30 22:08

import ckeditor_uploader.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('extra', '0008_auto_20210630_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='links',
            name='description',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
        migrations.AlterField(
            model_name='links',
            name='link',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
        migrations.AlterField(
            model_name='links',
            name='name',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
    ]