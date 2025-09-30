from enum import Enum
from typing import Optional

from pydantic import ConfigDict, EmailStr, Field, field_validator
from pydantic_settings import BaseSettings

from src.core.logger import temp_logger

logger = temp_logger()


try:

    class DBEngine(str, Enum):
        """Поддерживаемые движки баз данных для приложения."""

        SQLITE = 'sqlite'
        POSTGRES = 'postgres'
        POSTGRESQL = 'postgresql'

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
        db_engine: str = Field(
            default=DBEngine.POSTGRES.value,
            env='DB_ENGINE',
        )
        db_host: str = Field(..., env='DB_HOST')
        db_port: int = Field(..., env='DB_PORT')
        db_name: str = Field(..., env='DB_NAME')
        db_user: str = Field(..., env='DB_USER')
        db_password: str = Field(..., env='DB_PASSWORD')

        # -------------------
        # Настройки повторных попыток БД
        # -------------------
        db_retry_max_attempts: int = Field(
            default=3,
            env='DB_RETRY_MAX_ATTEMPTS',
        )
        db_retry_delay_seconds: float = Field(
            default=0.1,
            env='DB_RETRY_DELAY_SECONDS',
        )

        # -------------------
        # JWT / безопасность
        # -------------------
        secret: str = Field(..., env='SECRET')
        jwt_algorithm: str = Field(..., env='JWT_ALGORITHM')
        access_token_expire_minutes: int = Field(
            ...,
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
            if hasattr(self, 'database_uri') and getattr(
                self,
                'database_uri',
                None,
            ):
                return self.database_uri

            if self.db_engine in (
                DBEngine.POSTGRES.value,
                DBEngine.POSTGRESQL.value,
            ):
                return self._get_postgresql_uri()
            return self._get_sqlite_uri()

        def _get_sqlite_uri(self) -> str:
            """Возвращает URI для SQLite."""
            return f'sqlite+aiosqlite:///./{self.db_name}'

        def _get_postgresql_uri(self) -> str:
            """Возвращает URI для PostgreSQL."""
            if not all(
                [self.db_host, self.db_name, self.db_user, self.db_password],
            ):
                raise ValueError(
                    'Для PostgreSQL необходимо указать '
                    'host, name, user, password',
                )

            port = f':{self.db_port}' if self.db_port else ''
            return (
                f'postgresql+asyncpg://{self.db_user}:'
                f'{self.db_password}@{self.db_host}{port}/{self.db_name}'
            )

        @field_validator('db_engine')
        @classmethod
        def validate_db_engine(cls, value: str) -> str:
            """Проверяет допустимый тип базы данных."""
            value_clean = value.strip().lower()
            if value_clean not in [enum.value for enum in DBEngine]:
                raise ValueError(
                    'DB engine должен быть одним из: '
                    f'{", ".join(enum.value for enum in DBEngine)}',
                )
            return value_clean

        model_config = ConfigDict(
            env_file='.env',
            extra='allow',
            case_sensitive=False,
        )

    settings = Settings()
    """Глобальный объект конфигурации приложения."""
    logger.info(
        'Настройки загружены. DB URI: %s',
        settings.get_database_uri().replace(settings.db_password, '***'),
    )
except Exception as error:
    logger.exception(f'Ошибка при создании Settings: {error}')
    raise
