from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class BaseAPIException(HTTPException):
    """Базовое исключение для всех кастомных ошибок."""

    error_code: str = 'Error'

    def __init__(self, detail: str, status_code: int) -> None:
        """Инициализирует исключение с сообщением и HTTP-статусом."""
        super().__init__(status_code=status_code, detail=detail)

    def to_response(self) -> JSONResponse:
        """Возвращает JSON-ответ с кодом ошибки и сообщением."""
        return JSONResponse(
            status_code=self.status_code,
            content={
                'error': self.error_code,
                'message': self.detail,
            },
        )


class InvalidTokenException(BaseAPIException):
    """Недействительный токен."""

    error_code: str = 'InvalidToken'

    def __init__(self, detail: str = 'Недействительный токен') -> None:
        """Инициализирует исключение с кодом 401."""
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )


class ExpiredTokenException(BaseAPIException):
    """Истёкший токен."""

    error_code: str = 'ExpiredToken'

    def __init__(self, detail: str = 'Токен истёк') -> None:
        """Инициализирует исключение с кодом 401."""
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )


class UserNotFoundException(BaseAPIException):
    """Пользователь не найден."""

    error_code: str = 'UserNotFound'

    def __init__(self, detail: str = 'Пользователь не найден') -> None:
        """Инициализирует исключение с кодом 404."""
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class InvalidCredentialsException(BaseAPIException):
    """Неверный логин или пароль."""

    error_code: str = 'InvalidCredentials'

    def __init__(self, detail: str = 'Неверный логин или пароль') -> None:
        """Инициализирует исключение с кодом 401."""
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )


class PermissionDeniedException(BaseAPIException):
    """Недостаточно прав."""

    error_code: str = 'PermissionDenied'

    def __init__(self, detail: str = 'Недостаточно прав') -> None:
        """Инициализирует исключение с кодом 403."""
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Обработчик ошибок валидации запроса (422 → 400)."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'error': 'ValidationError',
            'message': 'Некорректные данные запроса',
            'details': exc.errors(),
        },
    )
