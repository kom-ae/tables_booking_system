from src.schemas.action import ActionDB
from src.schemas.bookings import Booking
from src.schemas.base import Error
from src.schemas.cafes import CafeDB
from src.schemas.dish import Dish

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


DISH_RESPONSES = {
    200: {
        'description': 'Данные блюда',
        'model': Dish,
    },
    201: {
        'description': 'Данные созданного блюда',
        'model': Dish,
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
        'description': 'Блюдо не найдено',
        'model': Error,
    },
}


BOOKING_RESPONSES = {
    200: {
        'description': 'Данные бронирования',
        'model': Booking,
    },
    201: {
        'description': 'Данные созданного бронирования',
        'model': Booking,
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
        'description': 'Бронирование не найдено',
        'model': Error,
    },
}
