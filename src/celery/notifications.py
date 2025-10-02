from src.core.logger import logger
from src.celery.app import celery_app


@celery_app.task
def send_notification(email: str) -> bool:
    logger.info('pass')
    return True
