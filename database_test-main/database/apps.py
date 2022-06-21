from django.apps import AppConfig


class Database(AppConfig):
    name = "database"

    def ready(self):
        import database.signals
