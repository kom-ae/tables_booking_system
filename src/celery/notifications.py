import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.core.logger import logger
from src.core.config import settings
from src.celery.app import celery_app


def read_html_template(template_name: str) -> str:
    """Read HTML template from file."""
    template_path = os.path.join(
        os.path.dirname(__file__), 'html', template_name
    )
    with open(template_path, 'r', encoding='utf-8') as file:
        return file.read()


@celery_app.task
def send_notification(email: str, cafe) -> bool:
    logger.info(f'Sending notification to {email}')

    try:
        html_template = read_html_template('client_notification.html')
    except Exception as e:
        logger.error(f"Ошибка при чтении шаблона: {e}")

    try:
        formatted_html = html_template.format(
            'pass'
        )
    except KeyError as e:
        logger.error(f"Ошибка форматирования HTML: отсутствует ключ {e}")

    msg = MIMEMultipart()
    msg['From'] = settings.email_login
    msg['To'] = email
    msg['Subject'] = 'Уведомление от кафе'
    msg.attach(MIMEText(formatted_html, 'html', 'utf-8'))

    try:
        with smtplib.SMTP_SSL(settings.email_ssl, 465) as server:
            server.login(settings.email_login, settings.email_password)
            server.send_message(msg)
        logger.info(f"Письмо успешно отправлено на {email}")
    except Exception as e:
        logger.error(f"Ошибка при отправке письма: {e}")
    return True
