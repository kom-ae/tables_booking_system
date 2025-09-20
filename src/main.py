from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from src.api import main_router
from src.api.exceptions.auth import (
    BaseAPIException,
    validation_exception_handler,
)
from src.api.exceptions.handlers import (
    base_api_exception_handler,
    user_exception_handler,
)
from src.api.exceptions.user import UserException
from src.constants import TAGS_METADATA
from src.core.config import settings
from src.core.init_db import create_first_superuser


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Инициализация БД и создание суперпользователя при старте приложения."""
    # await init_db()
    await create_first_superuser()
    yield


app = FastAPI(
    title=settings.app_title,
    description=settings.description,
    lifespan=lifespan,
    openapi_tags=TAGS_METADATA,
)

# Подключаем маршруты
app.include_router(main_router)

# Глобальные обработчики ошибок
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(UserException, user_exception_handler)
app.add_exception_handler(BaseAPIException, base_api_exception_handler)
