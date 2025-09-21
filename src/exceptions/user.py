from fastapi import status
from fastapi.responses import JSONResponse


class UserException(Exception):
    """Базовое исключение пользователя."""

    error_code: str = 'UserError'

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> None:
        """Инициализация исключения с сообщением и HTTP-статусом."""
        self.message = message
        self.status_code = int(status_code)
        super().__init__(message)

    def to_response(self) -> JSONResponse:
        """Возвращает JSON-ответ с ошибкой."""
        return JSONResponse(
            status_code=self.status_code,
            content={'error': self.error_code, 'message': self.message},
        )


class UserAlreadyExistsException(UserException):
    """Email или телефон уже занят."""

    error_code: str = 'UserAlreadyExists'

    def __init__(
        self,
        message: str = 'Пользователь с такими данными уже существует',
    ) -> None:
        """Инициализация исключения UserAlreadyExistsException."""
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class InvalidPhoneException(UserException):
    """Некорректный номер телефона."""

    error_code: str = 'InvalidPhone'

    def __init__(self, message: str = 'Некорректный номер телефона') -> None:
        """Инициализация исключения InvalidPhoneException."""
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class UserNotFoundException(UserException):
    """Пользователь не найден."""

    error_code: str = 'UserNotFound'

    def __init__(self, message: str = 'Пользователь не найден') -> None:
        """Инициализация исключения UserNotFoundException."""
        super().__init__(message, status.HTTP_404_NOT_FOUND)
