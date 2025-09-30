from src.schemas.action import ActionDB
from src.schemas.base import Error
from src.schemas.cafes import CafeDB

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
        'model': ActionDB,
    },
    201: {
        'description': 'Данные созданной акции',
        'model': ActionDB,
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
