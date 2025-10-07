"""Конфигурация для тестов с PostgreSQL."""

from enum import Enum
from typing import Optional

from pydantic import EmailStr, Field, field_validator
from pydantic_settings import BaseSettings

import logging

logger = logging.getLogger(__name__)


class DBEngine(str, Enum):
    """Поддерживаемые движки баз данных для приложения."""

    SQLITE = 'sqlite'
    POSTGRES = 'postgres'
    POSTGRESQL = 'postgresql'


class TestConfig(BaseSettings):
    """Настройки проекта для тестов."""

    # -------------------
    # Общие настройки
    # -------------------
    app_title: str = 'Сервис бронирования столиков (Test)'
    description: str = 'API для управления сервисом бронирования столиков (Test Environment)'
    debug: bool = True

    # -------------------
    # Настройки БД
    # -------------------
    db_engine: str = Field(
        default=DBEngine.POSTGRES.value,
        env='DB_ENGINE',
    )
    db_host: str = Field(default='localhost', env='DB_HOST')
    db_port: int = Field(default=5433, env='DB_PORT')  # Порт для тестовой БД
    db_name: str = Field(default='test_db', env='DB_NAME')
    db_user: str = Field(default='test_user', env='DB_USER')
    db_password: str = Field(default='test_password', env='DB_PASSWORD')

    # -------------------
    # PostgreSQL переменные (альтернативные)
    # -------------------
    postgres_host: str = Field(default='localhost', env='POSTGRES_HOST')
    postgres_port: int = Field(default=5433, env='POSTGRES_PORT')
    postgres_name: str = Field(default='test_db', env='POSTGRES_NAME')
    postgres_user: str = Field(default='test_user', env='POSTGRES_USER')
    postgres_password: str = Field(default='test_password', env='POSTGRES_PASSWORD')
    postgres_db: str = Field(default='test_db', env='POSTGRES_DB')

    # -------------------
    # JWT / безопасность
    # -------------------
    secret: str = Field(
        default='test_secret_key_for_testing_only',
        env='SECRET',
    )
    jwt_algorithm: str = Field(default='HS256', env='JWT_ALGORITHM')
    access_token_expire_minutes: int = Field(
        default=30,
        env='ACCESS_TOKEN_EXPIRE_MINUTES',
    )

    # -------------------
    # Первый суперпользователь
    # -------------------
    first_superuser_name: Optional[EmailStr] = Field(
        default=None,
        env='FIRST_SUPERUSER_USERNAME',
    )
    first_superuser_email: Optional[EmailStr] = Field(
        default=None,
        env='FIRST_SUPERUSER_EMAIL',
    )
    first_superuser_password: Optional[str] = Field(
        default=None,
        env='FIRST_SUPERUSER_PASSWORD',
    )
    first_superuser_role: Optional[str] = Field(
        default=None,
        env='FIRST_SUPERUSER_ROLE',
    )
    first_superuser_phone_number: Optional[str] = Field(
        default=None,
        env='FIRST_SUPERUSER_PHONE_NUMBER',
    )

    # -------------------
    # Логирование
    # -------------------
    log_file: str = Field(default='test.log', env='LOG_FILE')
    max_bytes: int = Field(default=1048576, env='MAX_BYTES')  # 1 MB
    backup_count: int = Field(default=1, env='BACKUP_COUNT')

    # -------------------
    # Методы
    # -------------------
    def get_database_uri(self) -> str:
        """Возвращает URI для подключения к базе данных."""
        if self.db_engine in (
            DBEngine.POSTGRES.value,
            DBEngine.POSTGRESQL.value,
        ):
            return self._get_postgresql_uri()
        return self._get_sqlite_uri()

    def get_test_database_uri(self, worker_id: str = None) -> str:
        """Возвращает URI для тестовой базы данных с учетом worker'а."""
        if self.db_engine in (
            DBEngine.POSTGRES.value,
            DBEngine.POSTGRESQL.value,
        ):
            return self._get_postgresql_test_uri(worker_id)
        return self._get_sqlite_test_uri(worker_id)

    def _get_sqlite_uri(self) -> str:
        """Возвращает URI для SQLite."""
        return f'sqlite+aiosqlite:///./test_{self.db_name}.db'

    def _get_postgresql_uri(self) -> str:
        """Возвращает URI для PostgreSQL."""
        # Используем POSTGRES_* переменные как fallback
        host = self.db_host or self.postgres_host
        port = self.db_port or self.postgres_port
        name = self.db_name or self.postgres_db or self.postgres_name
        user = self.db_user or self.postgres_user
        password = self.db_password or self.postgres_password

        port_str = f':{port}' if port else ''
        return (
            f'postgresql+asyncpg://{user}:'
            f'{password}@{host}{port_str}/{name}'
        )

    def _get_sqlite_test_uri(self, worker_id: str = None) -> str:
        """Возвращает URI для тестовой SQLite базы данных."""
        db_name = self.db_name or self.postgres_db or self.postgres_name
        if worker_id and worker_id != 'master':
            return f'sqlite+aiosqlite:///./test_{db_name}_{worker_id}.db'
        return f'sqlite+aiosqlite:///./test_{db_name}.db'

    def _get_postgresql_test_uri(self, worker_id: str = None) -> str:
        """Возвращает URI для тестовой PostgreSQL базы данных."""
        # Используем POSTGRES_* переменные как fallback
        host = self.db_host or self.postgres_host
        port = self.db_port or self.postgres_port
        name = self.db_name or self.postgres_db or self.postgres_name
        user = self.db_user or self.postgres_user
        password = self.db_password or self.postgres_password

        if worker_id and worker_id != 'master':
            name = f'{name}_{worker_id}'

        port_str = f':{port}' if port else ''
        return (
            f'postgresql+asyncpg://{user}:'
            f'{password}@{host}{port_str}/{name}'
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

    class Config:
        """Конфигурация Pydantic для работы с переменными окружения."""

        env_file = 'env.test'
        extra = 'allow'
        case_sensitive = False


# Глобальный объект конфигурации для тестов
test_settings = TestConfig()
logger.info(
    'Test settings loaded. DB URI: %s',
    test_settings.get_database_uri().replace(test_settings.db_password, '***'),
)
