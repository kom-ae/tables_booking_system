from fastapi import FastAPI

from src.api.endpoints import main_router
from src.core.config import settings

app: FastAPI = FastAPI(
    title=settings.app_title, description=settings.description,
)

app.include_router(main_router)
