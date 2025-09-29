from src.schemas.action import ActionsDB
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


ACTIONS_RESPONSES = {
    200: {
        'description': 'Данные акции',
        'model': ActionsDB,
    },
    201: {
        'description': 'Данные созданной акции',
        'model': ActionsDB,
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
        'description': 'Акция не найдена',
        'model': Error,
    },
}
