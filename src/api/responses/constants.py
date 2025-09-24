from src.schemas.base import Error
from src.schemas.cafes import CafeDB

# Описания кодов ответа для эндпоинта кафе.
CAFE_RESPONSES = {
    200: {
        'description': 'Данные кафе',
        'model': CafeDB,
    },
    201: {
        'description': 'Данные созданного кафе',
        'model': CafeDB,
    },
    400: {
        'description': 'Неверный формат запроса',
        'model': Error,
    },
    401: {
        'description': 'Необходима авторизация',
        'model': Error,
    },
    404: {
        'description': 'Кафе не найдено',
        'model': Error,
    },
}
