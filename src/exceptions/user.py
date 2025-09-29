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


class InvalidTelegramIDException(AppException):
    """Некорректный Telegram ID."""

    error_code: str = 'InvalidTelegramID'

    def __init__(self, message: str = 'TG ID некорректен') -> None:
        """Исключение 400."""
        super().__init__(message, status.HTTP_400_BAD_REQUEST)

    def to_response(self) -> JSONResponse:
        """JSON-ответ."""
        return JSONResponse(
            status_code=self.status_code,
            content={'error': self.error_code, 'message': self.message},
        )


class InvalidUsernameException(AppException):
    """Некорректный username."""

    error_code: str = 'InvalidUsername'

    def __init__(self, message: str = 'Username некорректен') -> None:
        """Исключение 400."""
        super().__init__(message, status.HTTP_400_BAD_REQUEST)

    def to_response(self) -> JSONResponse:
        """JSON-ответ."""
        return JSONResponse(
            status_code=self.status_code,
            content={'error': self.error_code, 'message': self.message},
        )


class InvalidEmailException(AppException):
    """Некорректный email."""

    error_code: str = 'InvalidEmail'

    def __init__(self, message: str = 'Email некорректен') -> None:
        """Исключение 400."""
        super().__init__(message, status.HTTP_400_BAD_REQUEST)

    def to_response(self) -> JSONResponse:
        """JSON-ответ."""
        return JSONResponse(
            status_code=self.status_code,
            content={'error': self.error_code, 'message': self.message},
        )


class PermissionDeniedException(AppException):
    """Нет прав доступа."""

    error_code: str = 'PermissionDenied'

    def __init__(self, message: str = 'Доступ запрещен') -> None:
        """Исключение 403."""
        super().__init__(message, status.HTTP_403_FORBIDDEN)

    def to_response(self) -> JSONResponse:
        """JSON-ответ."""
        return JSONResponse(
            status_code=self.status_code,
            content={'error': self.error_code, 'message': self.message},
        )


class ValidationException(AppException):
    """Ошибка валидации данных."""

    error_code: str = 'ValidationError'

    def __init__(
        self,
        message: str = 'Некорректные данные запроса',
        details: list = None,
    ) -> None:
        """Исключение 400."""
        self.details = details or []
        super().__init__(message, status.HTTP_400_BAD_REQUEST)

    def to_response(self) -> JSONResponse:
        """JSON-ответ."""
        content = {
            'error': self.error_code,
            'message': self.message,
            'details': self.details,
        }
        return JSONResponse(
            status_code=self.status_code,
            content=content,
        )
