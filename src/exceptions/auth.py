from fastapi import status

from src.exceptions.base import AppException


class InvalidTokenException(AppException):
    """Недействительный токен."""

    error_code: str = 'InvalidToken'

    def __init__(self, message: str = 'Недействительный токен') -> None:
        """Исключение."""
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class ExpiredTokenException(AppException):
    """Истёкший токен."""

    error_code: str = 'ExpiredToken'

    def __init__(self, message: str = 'Токен истёк') -> None:
        """Исключение."""
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class InvalidCredentialsException(AppException):
    """Неверные данные."""

    error_code: str = 'InvalidCredentials'

    def __init__(self, message: str = 'Неверный логин или пароль') -> None:
        """Исключение."""
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)
