from fastapi import status

from src.schemas.base import Error
from src.schemas.cafes import CafeDB


cafes_list_responses = {
    status.HTTP_200_OK: {
        'description': 'Список кафе',
        'model': list[CafeDB],
    },
    status.HTTP_400_BAD_REQUEST: {
        'description': 'Неверный формат запроса',
        'model': Error,
    },
    status.HTTP_401_UNAUTHORIZED: {
        'description': 'Необходима авторизация',
        'model': Error,
    },
}

cafe_create_responses = {
    status.HTTP_201_CREATED: {
        'description': 'Данные созданного кафе',
        'model': CafeDB,
    },
    status.HTTP_400_BAD_REQUEST: {
        'description': 'Неверный формат запроса',
        'model': Error,
    },
    status.HTTP_401_UNAUTHORIZED: {
        'description': 'Необходима авторизация',
        'model': Error,
    },
}

cafe_check_duplicate_responses = {
        'status_code': status.HTTP_400_BAD_REQUEST,
        'detail': 'Кафе с таким именем и адресом уже существует.',
}
