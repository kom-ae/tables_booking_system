import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.celery import types
from src.celery.app import celery_app
from src.core.config import settings
from src.core.logger import logger


def read_html_template(template_name: str) -> str:
    """Read HTML template from file."""
    template_path = os.path.join(
        os.path.dirname(__file__), 'html', template_name,
    )
    with open(template_path, 'r', encoding='utf-8') as file:
        return file.read()


@celery_app.task
def send_notification(
    booking: dict,
    notif_type: types.NotificationType,
) -> bool:
    """Универсальная таска для отправки e-mail уведомлений."""
    notif_type = types.NotificationType(notif_type)
    subject_client_msg, subject_manager_msg = types.SUBJECTS[notif_type]
    template_client, template_manager = types.TEMPLATES[notif_type]
    formatter_client, formatter_manager = types.FORMATTERS[notif_type]

    send_email(
        recipient=booking['user']['email'],
        subject=subject_client_msg,
        template_name=template_client,
        context=formatter_client(booking),
    )

    for manager in booking['cafe']['managers']:
        send_email(
            recipient=manager['email'],
            subject=subject_manager_msg,
            template_name=template_manager,
            context=formatter_manager(booking),
        )

    return True


def send_email(
        recipient: str, subject: str, template_name: str, context: dict,
) -> bool:
    """Отправляет e-mail сообщение."""
    try:
        html_template = read_html_template(template_name)
        formatted_html = html_template.format(**context)
    except Exception as e:
        logger.error(f'Ошибка при подготовке шаблона {template_name}: {e}')
        return False

    msg = MIMEMultipart()
    msg['From'] = settings.email_login
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(formatted_html, 'html', 'utf-8'))

    try:
        with smtplib.SMTP_SSL(settings.email_ssl, 465) as server:
            server.login(settings.email_login, settings.email_password)
            server.send_message(msg)
        logger.info(f'Письмо: {subject}. Успешно отправлено на {recipient}')
        return True
    except Exception as e:
        logger.error(f'Ошибка при отправке письма: {e}')
        return False
