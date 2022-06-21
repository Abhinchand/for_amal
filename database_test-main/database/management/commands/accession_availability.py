
from django.core.management.base import BaseCommand
from Bio import Entrez

# Import the model
from database.models import PesticidalProteinPrivateDatabase as PD
from extra.models import NCBIAvailability

Entrez.email = "admin@bpprc.org"


def _update_model(accession, availability):
    try:
        NCBIAvailability.objects.create(
            accession=accession, availability=availability)
    except:
        status = 'fail'
    else:
        status = 'success'
    return status


def check_ncbi(accession):
    try:
        handle = Entrez.efetch(
            db="nucleotide",
            id=accession,
            rettype="fasta",
            retmode="text",
        )
        return 'Public'
    except BaseException:
        return 'Private'


class Command(BaseCommand):
    help = "Checks NCBI accession public availability once 15 days"

    def handle(self, *args, **kwargs):
        print('Deleting the model...')
        NCBIAvailability.objects.all().delete()

        print('checking the availability in NCBI...')

        accessions = PD.objects.order_by("accession").values_list(
            "accession", flat=True).distinct().exclude(accession=None)

        for accession in accessions:
            print('Checking the NCBI status for the accession number:', accession)
            status = check_ncbi(accession)
            if status == 'Public':
                status = _update_model(accession, 'Public')
            if status == 'Private':
                status = _update_model(accession, 'Private')

        # availability = NCBIAvailability.objects.all()
        # for accession in availability:
        #     print("accession:", accession.accession)
        #     print("Public or private:", accession.availability)
