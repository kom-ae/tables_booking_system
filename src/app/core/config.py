from typing import Optional

from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    """Конфигурационные настройки для благотворительного фонда."""

    app_title: str = "Сервис бронирования столиков"
    description: str = ("API для управления сервисом бронирования столиков")
    database_uri: str = "sqlite+aiosqlite:///./fastapi.db"
    secret: str = "SECRET"
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None

    class Config:
        env_file: str = ".env"


settings: Settings = Settings()
