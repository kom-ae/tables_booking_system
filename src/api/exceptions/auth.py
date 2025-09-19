from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class BaseAPIException(HTTPException):
    """Базовое исключение для кастомных ошибок авторизации."""

    error_code: str = 'Error'

    def __init__(self, detail: str, status_code: int) -> None:
        """Инициализация с сообщением и HTTP-статусом."""
        super().__init__(status_code=status_code, detail=detail)

    def to_response(self) -> JSONResponse:
        """Возвращает JSON с ошибкой."""
        return JSONResponse(
            status_code=self.status_code,
            content={'error': self.error_code, 'message': self.detail},
        )


class InvalidTokenException(BaseAPIException):
    """Недействительный токен."""

    error_code: str = 'InvalidToken'

    def __init__(self, detail: str = 'Недействительный токен') -> None:
        """Инициализация InvalidTokenException."""
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail)


class ExpiredTokenException(BaseAPIException):
    """Истёкший токен."""

    error_code: str = 'ExpiredToken'

    def __init__(self, detail: str = 'Токен истёк') -> None:
        """Инициализация ExpiredTokenException."""
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail)


class InvalidCredentialsException(BaseAPIException):
    """Неверный логин или пароль."""

    error_code: str = 'InvalidCredentials'

    def __init__(self, detail: str = 'Неверный логин или пароль') -> None:
        """Инициализация InvalidCredentialsException."""
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail)


class PermissionDeniedException(BaseAPIException):
    """Недостаточно прав."""

    error_code: str = 'PermissionDenied'

    def __init__(self, detail: str = 'Недостаточно прав') -> None:
        """Инициализация PermissionDeniedException."""
        super().__init__(status.HTTP_403_FORBIDDEN, detail)


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Обработка ошибок валидации запроса (422 → 400)."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'error': 'ValidationError',
            'message': 'Некорректные данные запроса',
            'details': exc.errors(),
        },
    )
