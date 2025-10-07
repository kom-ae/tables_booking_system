from enum import Enum

from src.celery import formatters


class NotificationType(Enum):
    """Enum для распределения уведомлений."""

    CREATE = 'create'
    UPDATE = 'update'
    CANCEL = 'cancel'


SUBJECTS = {
    NotificationType.CREATE: (
        'Уведомление от кафе',
        'Уведомление о заказе',
    ),
    NotificationType.UPDATE: (
        'Обновленная информация по вашему бронированию',
        'Изменена информация по бронированию',
    ),
    NotificationType.CANCEL: (
        'Ваше бронирование отменено',
        'Бронирование отменено',
    ),
}

TEMPLATES = {
    NotificationType.CREATE: (
        'client_notification.html',
        'manager_notification.html',
    ),
    NotificationType.UPDATE: (
        'client_notification.html',
        'manager_notification.html',
    ),
    NotificationType.CANCEL: (
        'client_cancel_notification.html',
        'manager_cancel_notification.html',
    ),
}

FORMATTERS = {
    NotificationType.CREATE: (
        formatters.client_template_formatter,
        formatters.manager_template_formatter,
    ),
    NotificationType.UPDATE: (
        formatters.client_template_formatter,
        formatters.manager_template_formatter,
    ),
    NotificationType.CANCEL: (
        formatters.client_cancel_formatter,
        formatters.manager_cancel_formatter,
    ),
}
