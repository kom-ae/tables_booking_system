from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from src.api import main_router
from src.core.config import settings
from src.core.init_db import create_first_superuser, init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Создаёт суперпользователя при старте приложения."""
    await init_db()
    await create_first_superuser()
    yield


app: FastAPI = FastAPI(
    title=settings.app_title,
    description=settings.description,
    lifespan=lifespan,
)

app.include_router(main_router)
