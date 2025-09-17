from src.api import main_router
from src.core.config import settings
from fastapi import FastAPI

app: FastAPI = FastAPI(
    title=settings.app_title, description=settings.description,
)

app.include_router(main_router)
