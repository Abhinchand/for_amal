import csv

from django.conf.urls.static import settings
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile

# Import the model
from database.models import PesticidalProteinDatabase as PD


class Command(BaseCommand):
    help = "Writes data to fastasequence_files"

    def handle(self, *args, **kwargs):

        # Show this before loading the data into the database
        print("write media files")

        file_path = settings.MEDIA_ROOT + "/fastasequence_files/"
        print("file path", file_path)

        data = PD.objects.all()
        for item in data:
            filename = "{}".format(item.name)
            file_contents = ">{}\n{}\n".format(item.name, item.sequence)

            content = ContentFile(file_contents)
            item.fastasequence_file.save(filename, content, save=False)
