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
