from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.exceptions.auth import BaseAPIException
from src.exceptions.user import UserException


async def user_exception_handler(
    request: Request,
    exc: UserException,
) -> JSONResponse:
    """Универсальный обработчик ошибок пользователя."""
    return exc.to_response()


async def base_api_exception_handler(
    request: Request,
    exc: BaseAPIException,
) -> JSONResponse:
    """Универсальный обработчик ошибок авторизации и прав."""
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
