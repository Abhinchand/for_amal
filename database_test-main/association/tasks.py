from django.core.management import call_command
from celery import shared_task

# call_command('similar_proteins', verbosity=3, interactive=False)


@shared_task
def load_data_identical_proteins():
    try:
        call_command("upload_identical_proteins", verbosity=0)
        return "success"
    except IOError as e:
        return e
