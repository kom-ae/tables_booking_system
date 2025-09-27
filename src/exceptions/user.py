from fastapi import status
from fastapi.responses import JSONResponse

from src.exceptions.base import AppException


# === Пользовательские ошибки ===
class UserNotFoundException(AppException):
    """Пользователь не найден."""

    error_code: str = 'UserNotFound'

    def __init__(self, message: str = 'Пользователь не найден') -> None:
        """Исключение 404."""
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class InvalidPasswordException(AppException):
    """Некорректный пароль."""

    error_code: str = 'InvalidPassword'

    def __init__(
        self,
        message: str = 'Пароль не соответствует требованиям безопасности',
    ) -> None:
        """Исключение 400."""
        super().__init__(message, status.HTTP_400_BAD_REQUEST)

    def to_response(self) -> JSONResponse:
        """JSON-ответ."""
        return JSONResponse(
            status_code=self.status_code,
            content={'error': self.error_code, 'message': self.message},
        )


class InvalidPhoneException(AppException):
    """Некорректный телефон."""

    error_code: str = 'InvalidPhone'

    def __init__(self, message: str = 'Некорректный номер телефона') -> None:
        """Исключение 400."""
        super().__init__(message, status.HTTP_400_BAD_REQUEST)

    def to_response(self) -> JSONResponse:
        """JSON-ответ."""
        return JSONResponse(
            status_code=self.status_code,
            content={'error': self.error_code, 'message': self.message},
        )


# === Ошибки базы данных ===
class DBIntegrityException(AppException):
    """Ошибка целостности."""

    error_code: str = 'DBIntegrityError'

    def __init__(self, message: str = 'Ошибка целостности данных') -> None:
        """Исключение 400."""
        super().__init__(message, status.HTTP_400_BAD_REQUEST)

    def to_response(self) -> JSONResponse:
        """JSON-ответ с уточнением поля."""
        msg: str = self.message
        if 'UNIQUE constraint failed' in msg:
            field: str = msg.split(':')[-1].strip().split('.')[-1]
            msg = f'Пользователь с таким {field} уже существует'
        return JSONResponse(
            status_code=self.status_code,
            content={'error': self.error_code, 'message': msg},
        )


class DBException(AppException):
    """Ошибка БД."""

    error_code: str = 'DBError'

    def __init__(
        self,
        message: str = 'Ошибка базы данных',
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> None:
        """Исключение 500."""
        super().__init__(message, status_code)
