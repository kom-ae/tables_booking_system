from fastapi import Request
from fastapi.responses import JSONResponse

from src.api.exceptions.auth import BaseAPIException
from src.api.exceptions.user import UserException


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
