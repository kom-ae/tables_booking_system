from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from src.api import main_router
from src.constants import TAGS_METADATA
from src.core.config import settings
from src.core.init_db import init_db_and_superuser
from src.core.logger import logger
from src.exceptions.handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Инициализация БД и создание суперпользователя при старте приложения."""
    logger.info('Запуск приложения, инициализация БД и суперпользователя')
    await init_db_and_superuser()
    yield
    logger.info('Приложение завершает работу')


app = FastAPI(
    title=settings.app_title,
    description=settings.description,
    lifespan=lifespan,
    openapi_tags=TAGS_METADATA,
)

app.include_router(main_router)

register_exception_handlers(app)
