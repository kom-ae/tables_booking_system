from fastapi import status

from src.schemas.base import Error
from src.schemas.users import UserRead

users_list_responses = {
    status.HTTP_200_OK: {
        'description': 'Успешное получение списка пользователей',
        'model': list[UserRead],
    },
    status.HTTP_401_UNAUTHORIZED: {
        'description': 'Необходима авторизация',
        'model': Error,
    },
}

user_create_responses = {
    status.HTTP_201_CREATED: {
        'description': 'Данные созданного пользователя',
        'model': UserRead,
    },
    status.HTTP_400_BAD_REQUEST: {
        'description': 'Неверный формат запроса',
        'model': Error,
    },
}

user_update_responses = {
    status.HTTP_200_OK: {
        'description': 'Данные пользователя',
        'model': UserRead,
    },
    status.HTTP_401_UNAUTHORIZED: {
        'description': 'Необходима авторизация',
        'model': Error,
    },
    status.HTTP_404_NOT_FOUND: {
        'description': 'Пользователь не найден',
        'model': Error,
    },
}

current_user_get_responses = {
    status.HTTP_200_OK: {
        'description': 'Данные пользователя',
        'model': UserRead,
    },
    status.HTTP_401_UNAUTHORIZED: {
        'description': 'Необходима авторизация',
        'model': Error,
    },
    status.HTTP_404_NOT_FOUND: {
        'description': 'Пользователь не найден',
        'model': Error,
    },
}

current_user_update_responses = {
    status.HTTP_200_OK: {
        'description': 'Данные пользователя',
        'model': UserRead,
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
