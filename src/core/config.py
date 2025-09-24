from enum import Enum
from typing import Optional

from pydantic import EmailStr, field_validator
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
        database_uri: Optional[str] = None
        db_engine: str = DBEngine.SQLITE.value
        db_host: Optional[str] = None
        db_port: Optional[int] = None
        db_name: str = 'fastapi.db'
        db_user: Optional[str] = None
        db_password: Optional[str] = None

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

        # -------------------
        # Методы
        # -------------------

        @property
        def get_database_uri(self) -> str:
            """Возвращает полный URI для подключения к базе данных."""
            if self.database_uri:
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
            if not all([
                self.db_host, self.db_name,
                self.db_user, self.db_password,
            ]):
                raise ValueError(
                    'Для PostgreSQL необходимо указать host, name, user, '
                    'password',
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
            if value.lower() not in [e.value for e in DBEngine]:
                raise ValueError(
                    'DB engine должен быть одним из: '
                    f'{", ".join(e.value for e in DBEngine)}',
                )
            return value.lower()

        class Config:
            """Конфигурация Pydantic для работы с переменными окружения."""

            env_file = '.env'
            extra = 'allow'

    settings: Settings
    """Глобальный объект конфигурации приложения."""
    settings = Settings()

except Exception as error:
    logger.exception(f'Ошибка при создании Settings: {error}')
    raise
