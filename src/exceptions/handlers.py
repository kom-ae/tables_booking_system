from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from src.exceptions.base import AppException


async def base_api_exception_handler(
    request: Request,
    exc: AppException,
) -> JSONResponse:
    """Обработка всех кастомных исключений приложения."""
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


async def pydantic_validation_exception_handler(
    request: Request,
    exc: ValidationError,
) -> JSONResponse:
    """Обрабатывает ошибки валидации Pydantic моделей."""
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
            'message': 'Ошибка валидации данных',
            'details': errors,
        },
    )


async def global_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Обработчик непредвиденных ошибок (500)."""
    print(f'Unexpected error: {exc}')

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            'error': 'InternalServerError',
            'message': 'Внутренняя ошибка сервера',
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрация всех обработчиков исключений приложения."""
    app.add_exception_handler(AppException, base_api_exception_handler)
    app.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )
    app.add_exception_handler(
        ValidationError,
        pydantic_validation_exception_handler,
    )
    app.add_exception_handler(Exception, global_exception_handler)
