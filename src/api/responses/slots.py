from typing import Any, Dict, Union

from fastapi import status

from src.schemas.base import Error
from src.schemas.slots import SlotDB, SlotShortDB

HTTPCode = Union[int, str]
Responses = Dict[HTTPCode, Dict[str, Any]]

slots_list_responses: Responses = {
    status.HTTP_200_OK: {
        'description': 'Список слотов',
        'model': list[SlotShortDB],
    },
    status.HTTP_401_UNAUTHORIZED: {
        'description': 'Необходима авторизация',
        'model': Error,
    },
}

slot_get_responses: Responses = {
    status.HTTP_200_OK: {
        'description': 'Данные слота',
        'model': SlotDB,
    },
    status.HTTP_401_UNAUTHORIZED: {
        'description': 'Необходима авторизация',
        'model': Error,
    },
    status.HTTP_404_NOT_FOUND: {
        'description': 'Слот не найден',
        'model': Error,
    },
}

slot_create_responses: Responses = {
    status.HTTP_201_CREATED: {
        'description': 'Созданный слот',
        'model': SlotDB,
    },
    status.HTTP_400_BAD_REQUEST: {
        'description': 'Неверные данные',
        'model': Error,
    },
    status.HTTP_401_UNAUTHORIZED: {
        'description': 'Необходима авторизация',
        'model': Error,
    },
}

slot_update_responses: Responses = {
    status.HTTP_200_OK: {
        'description': 'Обновлённый слот',
        'model': SlotDB,
    },
    status.HTTP_400_BAD_REQUEST: {
        'description': 'Неверные данные',
        'model': Error,
    },
    status.HTTP_401_UNAUTHORIZED: {
        'description': 'Необходима авторизация',
        'model': Error,
    },
    status.HTTP_404_NOT_FOUND: {
        'description': 'Слот не найден',
        'model': Error,
    },
}

slot_delete_responses: Responses = {
    status.HTTP_204_NO_CONTENT: {
        'description': 'Удалено (soft delete)',
    },
    status.HTTP_401_UNAUTHORIZED: {
        'description': 'Необходима авторизация',
        'model': Error,
    },
    status.HTTP_404_NOT_FOUND: {
        'description': 'Слот не найден',
        'model': Error,
    },
}
