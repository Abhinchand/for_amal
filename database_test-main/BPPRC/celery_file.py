import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "BPPRC.settings")

celery_app = Celery("BPPRC", broker='amqp://guest@localhost//',
                    backend='amqp://guest@localhost//',
                    include=['association.tasks', 'bestmatchfinder.tasks', 'namingalgorithm.tasks'])
celery_app.config_from_object("django.conf.settings", namespace="CELERY")
celery_app.conf.update(CELERY_TASK_SERIALIZER='json',
                       CELERY_RESULT_SERIALIZER='json', CELERY_ACCEPT_CONTENT=['json'],
                       CELERY_TIMEZONE='Europe/London', CELERY_ENABLE_UTC=True)


# here is the beat schedule dictionary defined
celery_app.conf.beat_schedule = {
    "print-every-minute": {
        "task": "namingalgorithm.tasks.run",
        # "schedule": crontab(hour="*/1")
        "schedule": crontab(hour="23", minute="58")
        # 'args': ('Its Thursday!',)
    },
    # Execute every sunday
    "run-fetch-ncbi": {
        "task": "namingalgorithm.tasks.update_ncbi_accession_status",
        'schedule': crontab(hour="0", minute="0", day_of_week="sunday"),
    },
    # Execute every sunday
    "run-identical-proteins": {
        "task": "association.tasks.load_data_identical_proteins",
        'schedule': crontab(hour="0", minute="0", day_of_week="sunday"),
    },
}


celery_app.conf.timezone = "GMT"
celery_app.autodiscover_tasks()
