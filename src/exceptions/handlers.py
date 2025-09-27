from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.exceptions.auth import (
    ExpiredTokenException,
    InvalidCredentialsException,
    InvalidTokenException,
    PermissionDeniedException,
)
from src.exceptions.base import AppException
from src.exceptions.user import (
    DBIntegrityException,
    InvalidPasswordException,
    InvalidPhoneException,
    UserNotFoundException,
)


async def base_api_exception_handler(
    request: Request,
    exc: AppException,
) -> JSONResponse:
    """Обработчик для ошибок приложения (пользователи и авторизация)."""
    return exc.to_response()


async def invalid_token_exception_handler(
    request: Request,
    exc: InvalidTokenException,
) -> JSONResponse:
    """Обработчик для ошибок с недействительным токеном."""
    return exc.to_response()


async def expired_token_exception_handler(
    request: Request,
    exc: ExpiredTokenException,
) -> JSONResponse:
    """Обработчик для ошибок с истёкшим токеном."""
    return exc.to_response()


async def invalid_credentials_exception_handler(
    request: Request,
    exc: InvalidCredentialsException,
) -> JSONResponse:
    """Обработчик для ошибок с неверными логином или паролем."""
    return exc.to_response()


async def permission_denied_exception_handler(
    request: Request,
    exc: PermissionDeniedException,
) -> JSONResponse:
    """Обработчик для ошибок с недостаточными правами."""
    return exc.to_response()


async def user_not_found_exception_handler(
    request: Request,
    exc: UserNotFoundException,
) -> JSONResponse:
    """Обработчик для ошибок пользователя, не найденного в БД."""
    return exc.to_response()


async def db_integrity_exception_handler(
    request: Request,
    exc: DBIntegrityException,
) -> JSONResponse:
    """Обработчик для ошибок базы данных, связанных с целостностью данных."""
    return exc.to_response()


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Обрабатывает ошибки валидации запроса и возвращает JSON 400."""
    errors = [
        {
            'loc': err.get('loc', []),
            'msg': err.get('msg', ''),
            'type': err.get('type', ''),
        }
        for err in exc.errors()
    ]

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'error': 'ValidationError',
            'message': 'Некорректные данные запроса',
            'details': errors,
        },
    )


async def invalid_phone_exception_handler(
    request: Request,
    exc: InvalidPhoneException,
) -> JSONResponse:
    """Обработчик ошибки некорректного номера телефона."""
    return exc.to_response()


async def invalid_password_exception_handler(
    request: Request,
    exc: InvalidPasswordException,
) -> JSONResponse:
    """Обработчик ошибки некорректного пароля."""
    return exc.to_response()
