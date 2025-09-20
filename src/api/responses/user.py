from fastapi import status

from src.schemas.base import BaseError
from src.schemas.user import UserRead

users_list_responses = {
    status.HTTP_200_OK: {
        'description': 'Успешное получение списка пользователей',
        'model': list[UserRead],
    },
    status.HTTP_401_UNAUTHORIZED: {
        'description': 'Необходима авторизация',
        'model': BaseError,
    },
}

user_create_responses = {
    status.HTTP_201_CREATED: {
        'description': 'Данные созданного пользователя',
        'model': UserRead,
    },
    status.HTTP_400_BAD_REQUEST: {
        'description': 'Неверный формат запроса',
        'model': BaseError,
    },
}


user_update_responses = {
    status.HTTP_200_OK: {
        'description': 'Данные пользователя',
        'model': UserRead,
    },
    status.HTTP_401_UNAUTHORIZED: {
        'description': 'Необходима авторизация',
        'model': BaseError,
    },
    status.HTTP_404_NOT_FOUND: {
        'description': 'Пользователь не найден',
        'model': BaseError,
    },
}

current_user_get_responses = {
    status.HTTP_200_OK: {
        'description': 'Данные пользователя',
        'model': UserRead,
    },
    status.HTTP_401_UNAUTHORIZED: {
        'description': 'Необходима авторизация',
        'model': BaseError,
    },
}

current_user_update_responses = {
    status.HTTP_200_OK: {
        'description': 'Данные пользователя',
        'model': UserRead,
    },
    status.HTTP_400_BAD_REQUEST: {
        'description': 'Неверный формат запроса',
        'model': BaseError,
    },
    status.HTTP_401_UNAUTHORIZED: {
        'description': 'Необходима авторизация',
        'model': BaseError,
    },
}
