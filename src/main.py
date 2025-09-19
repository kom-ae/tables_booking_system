from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError

from src.api import main_router
from src.api.exceptions.auth import (
    BaseAPIException,
    validation_exception_handler,
)
from src.core.config import settings
from src.core.init_db import create_first_superuser, init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Инициализация БД и создание суперпользователя при старте приложения."""
    await init_db()
    await create_first_superuser()
    yield


app: FastAPI = FastAPI(
    title=settings.app_title,
    description=settings.description,
    lifespan=lifespan,
)

# Подключаем маршруты
app.include_router(main_router)

# Глобальные обработчики ошибок
app.add_exception_handler(RequestValidationError, validation_exception_handler)


@app.exception_handler(BaseAPIException)
async def base_api_exception_handler(
    request: Request,
    exc: BaseAPIException,
) -> dict:
    """Единый обработчик кастомных исключений с унифицированным ответом."""
    return exc.to_response()
