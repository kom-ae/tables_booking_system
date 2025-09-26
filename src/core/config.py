from typing import Optional

from pydantic import EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Конфигурационные настройки приложения."""

    # -------------------
    # Общие настройки приложения
    # -------------------
    app_title: str = 'Сервис бронирования столиков'
    description: str = 'API для управления сервисом бронирования столиков'
    debug: bool = True

    # -------------------
    # База данных
    # -------------------
    database_uri: str = 'sqlite+aiosqlite:///./fastapi.db'

    # -------------------
    # JWT / безопасность
    # -------------------
    secret: str = 'SECRET'
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 120

    # -------------------
    # Первый суперпользователь
    # -------------------
    first_superuser_name: Optional[EmailStr] = None
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None
    first_superuser_role: Optional[str] = None
    first_superuser_phone_number: Optional[str] = None

    # -------------------
    # Логирование
    # -------------------
    log_file: Optional[str] = None
    max_bytes: Optional[int] = None
    backup_count: Optional[int] = None
    system_username: Optional[str] = None

    # -------------------
    # Прочие
    # -------------------
    default_user_id: Optional[int] = None

    class Config:
        """Настройки Pydantic для работы с переменными окружения."""

        env_file = '.env'
        extra = 'allow'


settings: Settings = Settings()
