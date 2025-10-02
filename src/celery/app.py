from celery import Celery

from src.core.config import settings

celery_app = Celery(
    settings.app_title + '- TASKS',
    broker=settings.celery_broker_url,
    backend=settings.celery_backend_url
)
