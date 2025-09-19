from typing import Optional

from pydantic import EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Конфигурационные настройки."""

    app_title: str = 'Сервис бронирования столиков'
    description: str = 'API для управления сервисом бронирования столиков'
    database_uri: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = 'SECRET'
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 120
    first_superuser_name: Optional[EmailStr] = None
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None
    first_superuser_role: Optional[str] = None
    first_superuser_phone_number: Optional[str] = None
    debug: bool = True

    class Config:
        """Настройки Pydantic для работы с переменными окружения."""

        env_file: str = '.env'
        extra = 'allow'


settings: Settings = Settings()
