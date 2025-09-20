from fastapi import status

from src.schemas.base import BaseError

login_responses = {
    status.HTTP_200_OK: {'description': 'Успешная аутентификация'},
    status.HTTP_401_UNAUTHORIZED: {
        'description': 'Неверный логин или пароль',
        'model': BaseError,
    },
}

logout_responses = {
    status.HTTP_200_OK: {'description': 'Успешный выход из аккаунта'},
    status.HTTP_401_UNAUTHORIZED: {
        'description': 'Необходима авторизация',
        'model': BaseError,
    },
}
