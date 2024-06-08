from django.apps import AppConfig


class LopeappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'lopeApp'

    def ready(self):
        import lopeApp.signals