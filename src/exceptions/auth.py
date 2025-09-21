from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


class BaseAPIException(HTTPException):
    """Базовое исключение для кастомных ошибок авторизации."""

    error_code: str = 'Error'

    def __init__(self, detail: str, status_code: int) -> None:
        """Инициализация исключения с сообщением и HTTP-статусом."""
        self.status_code = int(status_code)
        self.detail = detail
        super().__init__(status_code=self.status_code, detail=self.detail)

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
        """Инициализация исключения InvalidTokenException."""
        super().__init__(detail, status.HTTP_401_UNAUTHORIZED)


class ExpiredTokenException(BaseAPIException):
    """Истёкший токен."""

    error_code: str = 'ExpiredToken'

    def __init__(self, detail: str = 'Токен истёк') -> None:
        """Инициализация исключения ExpiredTokenException."""
        super().__init__(detail, status.HTTP_401_UNAUTHORIZED)


class InvalidCredentialsException(BaseAPIException):
    """Неверный логин или пароль."""

    error_code: str = 'InvalidCredentials'

    def __init__(self, detail: str = 'Неверный логин или пароль') -> None:
        """Инициализация исключения InvalidCredentialsException."""
        super().__init__(detail, status.HTTP_401_UNAUTHORIZED)


class PermissionDeniedException(BaseAPIException):
    """Недостаточно прав."""

    error_code: str = 'PermissionDenied'

    def __init__(self, detail: str = 'Недостаточно прав') -> None:
        """Инициализация исключения PermissionDeniedException."""
        super().__init__(detail, status.HTTP_403_FORBIDDEN)
