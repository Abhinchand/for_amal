from django.conf.urls.static import settings
from django.core.management.base import BaseCommand
from collections import defaultdict

# Import the model
from association.models import IdenticalProteins as PD

dict_data = defaultdict(list)

ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload the IdenticalProteins data from the CSV file, first delete the POSTGRES data file to destroy the database. Then, run `python manage.py migrate` for a new empty
database with tables"""


class Command(BaseCommand):
    help = "Loads data from identicalproteins.csv"

    def handle(self, *args, **kwargs):

        file_path = settings.MEDIA_ROOT + "/csv_files/identicalproteins.csv"
        print("file path", file_path)
        # Show this if the data already exist in the database
        if PD.objects.exists():
            PD.objects.all().delete()

        # Show this before loading the data into the database
        print("Loading IdenticalProteins data")

        # Load the data into the database
        fields = [
            "proteins",
        ]

        with open(file_path) as the_file:
            for line in the_file:
                string = line.split(',')
                string_1 = string[0].strip()
                string_2 = string[1].strip()
                dict_data[string_1].append(string_2)

        for key in dict_data.keys():
            similar_proteins = []
            similar_proteins.append(key)
            for protein in dict_data[key]:
                similar_proteins.append(protein)
            print(similar_proteins)
            PD.objects.create(proteins=similar_proteins)
