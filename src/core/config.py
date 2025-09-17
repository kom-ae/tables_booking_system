from typing import Optional

from pydantic import EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Конфигурационные настройки для НЕблаготворительного фонда."""

    app_title: str = "Сервис бронирования столиков"
    description: str = ("API для управления сервисом бронирования столиков")
    database_uri: str = "sqlite+aiosqlite:///./fastapi.db"
    secret: str = "SECRET"
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None

    class Config:
        """Конфиг класса."""

        env_file: str = ".env"


settings: Settings = Settings()
