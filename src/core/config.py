from enum import Enum
from typing import Optional

from pydantic import ConfigDict, EmailStr, Field
from pydantic_settings import BaseSettings


class DBEngine(str, Enum):
    """Поддерживаемые движки баз данных для приложения."""

    SQLITE = 'sqlite'
    POSTGRES = 'postgres'


class Settings(BaseSettings):
    """Настройки проекта."""

    # -------------------
    # Общие настройки
    # -------------------
    app_title: str = 'Сервис бронирования столиков'
    description: str = 'API для управления сервисом бронирования столиков'
    debug: bool = True

    # -------------------
    # Настройки БД
    # -------------------
    db_engine: DBEngine = Field(default=DBEngine.POSTGRES, env='DB_ENGINE')
    db_host: str = Field(..., env='DB_HOST')
    db_port: int = Field(..., env='DB_PORT')
    db_name: str = Field(..., env='DB_NAME')
    db_user: str = Field(..., env='DB_USER')
    db_password: str = Field(..., env='DB_PASSWORD')

    # -------------------
    # Настройки повторных попыток БД
    # -------------------
    db_retry_max_attempts: int = Field(..., env='DB_RETRY_MAX_ATTEMPTS')
    db_retry_delay_seconds: float = Field(..., env='DB_RETRY_DELAY_SECONDS')

    # -------------------
    # JWT / безопасность
    # -------------------
    secret: str = Field(..., env='SECRET')
    jwt_algorithm: str = Field(..., env='JWT_ALGORITHM')
    access_token_expire_minutes: int = Field(
        1,
        env='ACCESS_TOKEN_EXPIRE_MINUTES',
    )

    # -------------------
    # Первый суперпользователь
    # -------------------
    first_superuser_name: Optional[str] = None
    first_superuser_email: Optional[EmailStr] = None
    first_superuser_password: Optional[str] = None
    first_superuser_role: Optional[str] = None
    first_superuser_phone_number: Optional[str] = None

    # -------------------
    # Методы
    # -------------------
    def get_database_uri(self) -> str:
        """Возвращает URI для подключения к базе данных."""
        if self.db_engine == DBEngine.POSTGRES:
            return (
                f'postgresql+asyncpg://{self.db_user}:{self.db_password}'
                f'@{self.db_host}:{self.db_port}/{self.db_name}'
            )
        return f'sqlite+aiosqlite:///./{self.db_name}'

    model_config = ConfigDict(
        env_file='.env',
        extra='allow',
        case_sensitive=False,
    )


settings = Settings()
