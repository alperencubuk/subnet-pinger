from os import environ

from celery import Celery

environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.broker_connection_retry_on_startup = True
app.autodiscover_tasks()
