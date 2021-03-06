# Generated by Django 3.1.3 on 2021-08-06 12:11

import ckeditor_uploader.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('extra', '0020_ncbiavailability'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='faqeditheading',
            options={'verbose_name': 'Add FAQ Heading', 'verbose_name_plural': 'Add FAQ Headings'},
        ),
        migrations.RemoveField(
            model_name='faqedit',
            name='heading',
        ),
        migrations.AddField(
            model_name='faqedit',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='faqs', to='extra.faqeditheading'),
        ),
        migrations.AlterField(
            model_name='faqeditheading',
            name='category',
            field=ckeditor_uploader.fields.RichTextUploadingField(),
        ),
    ]
