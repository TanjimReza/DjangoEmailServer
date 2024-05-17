from django.apps import AppConfig
from django.conf import settings


class OtphomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'otphome'


    def ready(self):
        from .tasks import check_emails
        if settings.REFRESH_TIME_SECONDS:
            check_emails(repeat=settings.REFRESH_TIME_SECONDS)
