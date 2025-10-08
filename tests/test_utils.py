"""Утилиты для транзакционных тестов.

Этот модуль содержит утилиты для работы с транзакциями в тестах,
обеспечивающие изоляцию между тестами.
"""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, TypeVar

import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool

from tests.test_config import test_settings

T = TypeVar('T')


class TransactionalTestSession:
    """Класс для управления транзакционными сессиями."""

    def __init__(self):
        self.engine = create_async_engine(
            test_settings.get_database_uri(),
            echo=False,
            future=True,
            poolclass=NullPool,
            pool_pre_ping=True,
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Контекстный менеджер для транзакционной сессии."""
        async with self.session_factory() as session:
            # Начинаем транзакцию
            transaction = await session.begin()
            try:
                yield session
            except Exception:
                # Если произошла ошибка, откатываем транзакцию
                await transaction.rollback()
                raise
            finally:
                # Всегда откатываем транзакцию в конце
                await transaction.rollback()
                await session.close()

    async def cleanup(self):
        """Очистка ресурсов."""
        await self.engine.dispose()


# Глобальный экземпляр для использования в тестах
transactional_session = TransactionalTestSession()


@pytest_asyncio.fixture
async def isolated_session() -> AsyncGenerator[AsyncSession, None]:
    """Фикстура для изолированной сессии базы данных."""
    async with transactional_session.session() as session:
        yield session


@pytest_asyncio.fixture
async def isolated_client(
    isolated_session: AsyncSession,
) -> AsyncGenerator[Any, None]:
    """Фикстура для клиента с изолированной сессией."""
    from httpx import ASGITransport, AsyncClient
    from src.core.db import get_async_session
    from src.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url='http://testserver',
    ) as client:
        app.dependency_overrides[get_async_session] = lambda: isolated_session
        yield client
        app.dependency_overrides.clear()


class DatabaseIsolation:
    """Класс для обеспечения изоляции базы данных между тестами."""

    @staticmethod
    async def truncate_all_tables(session: AsyncSession) -> None:
        """Очищает все таблицы в правильном порядке из-за внешних ключей."""
        # Порядок очистки важен из-за внешних ключей
        tables_to_clean = [
            'cafe_manager',  # Ассоциативная таблица
            'booking',  # Когда будет реализовано
            'dishes',  # Когда будет реализовано
            'tables',  # Когда будет реализовано
            'time_slots',  # Когда будет реализовано
            'actions',  # Когда будет реализовано
            'cafes',
            'user',
        ]

        for table in tables_to_clean:
            try:
                await session.execute(text(f'TRUNCATE TABLE {table} CASCADE;'))
            except Exception:
                # Игнорируем ошибки для несуществующих таблиц
                pass

        await session.flush()

    @staticmethod
    async def reset_sequences(session: AsyncSession) -> None:
        """Сбрасывает последовательности (sequences) в PostgreSQL."""
        try:
            # Получаем все последовательности
            result = await session.execute(
                text(
                    """
                SELECT sequence_name 
                FROM information_schema.sequences 
                WHERE sequence_schema = 'public'
            """
                )
            )

            sequences = [row[0] for row in result.fetchall()]

            # Сбрасываем каждую последовательность
            for sequence in sequences:
                await session.execute(
                    text(f"ALTER SEQUENCE {sequence} RESTART WITH 1;")
                )

            await session.flush()
        except Exception:
            # Игнорируем ошибки если это не PostgreSQL
            pass


@pytest_asyncio.fixture
async def clean_database(
    isolated_session: AsyncSession,
) -> AsyncGenerator[None, None]:
    """Фикстура для очистки базы данных перед каждым тестом."""
    # Очистка перед тестом
    await DatabaseIsolation.truncate_all_tables(isolated_session)
    await DatabaseIsolation.reset_sequences(isolated_session)

    yield

    # Очистка после теста (хотя транзакция будет откачена)
    await DatabaseIsolation.truncate_all_tables(isolated_session)
    await DatabaseIsolation.reset_sequences(isolated_session)


class TestDataFactory:
    """Фабрика для создания тестовых данных с уникальными идентификаторами."""

    @staticmethod
    def generate_unique_email(base_email: str = "test@example.com") -> str:
        """Генерирует уникальный email."""
        import uuid

        unique_suffix = str(uuid.uuid4())[:8]
        return f"{unique_suffix}_{base_email}"

    @staticmethod
    def generate_unique_phone(base_phone: str = "+70000000001") -> str:
        """Генерирует уникальный номер телефона."""
        import uuid

        unique_suffix = str(uuid.uuid4())[:8]
        return f"+7000000{unique_suffix}"

    @staticmethod
    def generate_unique_username(base_username: str = "testuser") -> str:
        """Генерирует уникальное имя пользователя."""
        import uuid

        unique_suffix = str(uuid.uuid4())[:8]
        return f"{base_username}_{unique_suffix}"

    @staticmethod
    def generate_unique_cafe_name(base_name: str = "Test Cafe") -> str:
        """Генерирует уникальное название кафе."""
        import uuid

        unique_suffix = str(uuid.uuid4())[:8]
        return f"{base_name} {unique_suffix}"


# Утилиты для параллельного выполнения тестов
class ParallelTestUtils:
    """Утилиты для работы с параллельными тестами."""

    @staticmethod
    def get_worker_id() -> str:
        """Возвращает ID текущего worker'а для pytest-xdist."""
        import os

        return os.environ.get('PYTEST_XDIST_WORKER', 'master')

    @staticmethod
    def is_parallel_execution() -> bool:
        """Проверяет, выполняется ли тест в параллельном режиме."""
        return ParallelTestUtils.get_worker_id() != 'master'

    @staticmethod
    def get_test_database_name() -> str:
        """Возвращает имя базы данных для текущего worker'а."""
        worker_id = ParallelTestUtils.get_worker_id()
        if worker_id == 'master':
            return 'test_db'
        return f'test_db_{worker_id}'


# Декораторы для маркировки тестов
def parallel_test(func):
    """Декоратор для маркировки тестов, которые могут выполняться параллельно."""
    import pytest
    return pytest.mark.parallel(func)


def serial_test(func):
    """Декоратор для маркировки тестов, которые должны выполняться последовательно."""
    import pytest
    return pytest.mark.serial(func)


def integration_test(func):
    """Декоратор для маркировки интеграционных тестов."""
    import pytest
    return pytest.mark.integration(func)


def unit_test(func):
    """Декоратор для маркировки unit тестов."""
    import pytest
    return pytest.mark.unit(func)
