import csv

from django.conf.urls.static import settings
from django.core.management.base import BaseCommand

# Import the model
from database.models import PesticidalProteinPrivateDatabase as PD

ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload the PesticidalProteinPrivateDatabase data from the CSV file, first delete the POSTGRES data file to destroy the database. Then, run `python manage.py migrate` for a new empty
database with tables"""


class Command(BaseCommand):
    help = "Loads data from PesticidalProteinPrivateDatabase.csv. Please provide filename along with the path"

    def add_arguments(self, parser):
        parser.add_argument("filename", type=str, help="filename for csv file")

    def handle(self, *args, **kwargs):
        filename = kwargs["filename"]

        file_path = filename
        print("file path", file_path)
        # Show this if the data already exist in the database
        if PD.objects.exists():
            print("Data already loaded...exiting.")
            print(ALREDY_LOADED_ERROR_MESSAGE)
            return

        # Show this before loading the data into the database
        print("Loading PesticidalProteinPrivateDatabase data")

        # Load the data into the database
        fields = [
            "submittersname",
            "submittersemail",
            "name",
            "sequence",
            "bacterium",
            "bacterium_textbox",
            "taxonid",
            "year",
            "accession",
            "partnerprotein",
            "partnerprotein_textbox",
            "toxicto",
            "nontoxic",
            "dnasequence",
            "pdbcode",
            "publication",
            "comment",
            # "uploaded",
            "terms_conditions",
            # "admin_user",
            "admin_comments",
            "public",
            "oldname",
            # "created_by",
            # "created_on",
            # "edited_on",
        ]
        file_path = filename
        print("file path", file_path)
        raw_data = open(file_path, "rt", encoding="utf-8-sig")
        for row in csv.reader(raw_data):
            PD.objects.create(**dict(zip(fields, row)))
