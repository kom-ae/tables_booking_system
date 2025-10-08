"""Система управления тестовыми базами данных для параллельного выполнения.

Этот модуль обеспечивает создание и управление отдельными базами данных
для каждого worker'а при параллельном выполнении тестов.
"""

import os
from typing import Dict, List

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import NullPool

from tests.test_config import test_settings


class TestDatabaseManager:
    """Менеджер для управления тестовыми базами данных."""

    def __init__(self):
        self.engines: Dict[str, AsyncEngine] = {}
        self.created_databases: List[str] = []

    def get_worker_id(self) -> str:
        """Возвращает ID текущего worker'а."""
        return os.environ.get('PYTEST_XDIST_WORKER', 'master')

    def get_database_name(self, worker_id: str | None = None) -> str:
        """Возвращает имя базы данных для worker'а."""
        if worker_id is None:
            worker_id = self.get_worker_id()

        if worker_id == 'master':
            return test_settings.db_name
        return f"{test_settings.db_name}_{worker_id}"

    def get_engine(self, worker_id: str | None = None) -> AsyncEngine:
        """Возвращает движок базы данных для worker'а."""
        if worker_id is None:
            worker_id = self.get_worker_id()

        if worker_id not in self.engines:
            database_uri = test_settings.get_test_database_uri(worker_id)
            self.engines[worker_id] = create_async_engine(
                database_uri,
                echo=False,
                future=True,
                poolclass=NullPool,
                pool_pre_ping=True,
            )

        return self.engines[worker_id]

    async def create_database(self, worker_id: str | None = None) -> None:
        """Создает базу данных для worker'а."""
        if worker_id is None:
            worker_id = self.get_worker_id()

        if worker_id == 'master':
            return  # Основная база данных уже существует

        database_name = self.get_database_name(worker_id)

        # Создаем подключение к основной базе данных для создания новой
        main_engine = create_async_engine(
            test_settings.get_database_uri(),
            echo=False,
            future=True,
            poolclass=NullPool,
        )

        try:
            async with main_engine.connect() as conn:
                # Устанавливаем AUTOCOMMIT для создания БД
                await conn.execution_options(isolation_level='AUTOCOMMIT')

                # Проверяем, существует ли база данных
                result = await conn.execute(
                    text('SELECT 1 FROM pg_database WHERE datname = :db_name'),
                    {'db_name': database_name},
                )

                if not result.fetchone():
                    # Создаем базу данных
                    await conn.execute(
                        text(f"CREATE DATABASE {database_name}")
                    )
                    self.created_databases.append(database_name)
                    print(f"Created database: {database_name}")
                else:
                    print(f"Database already exists: {database_name}")

        finally:
            await main_engine.dispose()

    async def drop_database(self, worker_id: str | None = None) -> None:
        """Удаляет базу данных для worker'а."""
        if worker_id is None:
            worker_id = self.get_worker_id()

        if worker_id == 'master':
            return  # Не удаляем основную базу данных

        database_name = self.get_database_name(worker_id)

        if database_name not in self.created_databases:
            return

        # Создаем подключение к основной базе данных для удаления
        main_engine = create_async_engine(
            test_settings.get_database_uri(),
            echo=False,
            future=True,
            poolclass=NullPool,
        )

        try:
            async with main_engine.connect() as conn:
                # Устанавливаем AUTOCOMMIT для удаления БД
                await conn.execution_options(isolation_level='AUTOCOMMIT')

                # Завершаем все активные соединения
                await conn.execute(
                    text(
                        """
                    SELECT pg_terminate_backend(pid)
                    FROM pg_stat_activity
                    WHERE datname = :db_name AND pid <> pg_backend_pid()
                """
                    ),
                    {'db_name': database_name},
                )

                # Удаляем базу данных
                await conn.execute(
                    text(f"DROP DATABASE IF EXISTS {database_name}")
                )
                print(f"Dropped database: {database_name}")

        finally:
            await main_engine.dispose()

    async def cleanup_all_databases(self) -> None:
        """Очищает все созданные базы данных."""
        for database_name in self.created_databases:
            try:
                # Создаем подключение к основной базе данных
                main_engine = create_async_engine(
                    test_settings.get_database_uri(),
                    echo=False,
                    future=True,
                    poolclass=NullPool,
                )

                try:
                    async with main_engine.connect() as conn:
                        # Устанавливаем AUTOCOMMIT для удаления БД
                        await conn.execution_options(isolation_level='AUTOCOMMIT')

                        # Завершаем все активные соединения
                        await conn.execute(
                            text(
                                """
                            SELECT pg_terminate_backend(pid)
                            FROM pg_stat_activity
                            WHERE datname = :db_name AND pid <> pg_backend_pid()
                        """
                            ),
                            {'db_name': database_name},
                        )

                        # Удаляем базу данных
                        await conn.execute(
                            text(f"DROP DATABASE IF EXISTS {database_name}")
                        )
                        print(f"Dropped database: {database_name}")

                finally:
                    await main_engine.dispose()

            except Exception as e:
                print(f"Error dropping database {database_name}: {e}")

        self.created_databases.clear()

    async def dispose_all_engines(self) -> None:
        """Закрывает все движки базы данных."""
        for engine in self.engines.values():
            await engine.dispose()
        self.engines.clear()


# Глобальный экземпляр менеджера
db_manager = TestDatabaseManager()


class DatabaseCleanup:
    """Класс для очистки базы данных между тестами."""

    @staticmethod
    async def truncate_all_tables(engine: AsyncEngine) -> None:
        """Очищает все таблицы в правильном порядке."""
        # Порядок очистки важен из-за внешних ключей
        tables_to_clean = [
            'cafe_manager',  # Ассоциативная таблица
            'booking',  # Будет реализовано
            'dishes',  # Будет реализовано
            'tables',  # Будет реализовано
            'time_slots',  # Будет реализовано
            'actions',  # Будет реализовано
            'cafes',
            'user',
        ]

        async with engine.begin() as conn:
            for table in tables_to_clean:
                try:
                    await conn.execute(
                        text(f"TRUNCATE TABLE {table} CASCADE;")
                    )
                except Exception:
                    # Игнорируем ошибки для несуществующих таблиц
                    pass

    @staticmethod
    async def reset_sequences(engine: AsyncEngine) -> None:
        """Сбрасывает последовательности (sequences) в PostgreSQL."""
        try:
            async with engine.begin() as conn:
                # Получаем все последовательности
                result = await conn.execute(
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
                    await conn.execute(
                        text(f"ALTER SEQUENCE {sequence} RESTART WITH 1;")
                    )

        except Exception:
            # Игнорируем ошибки если это не PostgreSQL
            pass

    @staticmethod
    async def full_cleanup(engine: AsyncEngine) -> None:
        """Выполняет полную очистку базы данных."""
        await DatabaseCleanup.truncate_all_tables(engine)
        await DatabaseCleanup.reset_sequences(engine)


# Утилиты для работы с параллельными тестами
class ParallelTestDatabase:
    """Утилиты для работы с базами данных в параллельных тестах."""

    @staticmethod
    def get_current_database_uri() -> str:
        """Возвращает URI текущей базы данных."""
        worker_id = db_manager.get_worker_id()
        return test_settings.get_test_database_uri(worker_id)

    @staticmethod
    def get_current_engine() -> AsyncEngine:
        """Возвращает движок текущей базы данных."""
        worker_id = db_manager.get_worker_id()
        return db_manager.get_engine(worker_id)

    @staticmethod
    async def ensure_database_exists() -> None:
        """Убеждается, что база данных для текущего worker'а существует."""
        worker_id = db_manager.get_worker_id()
        await db_manager.create_database(worker_id)

    @staticmethod
    async def cleanup_current_database() -> None:
        """Очищает текущую базу данных."""
        engine = ParallelTestDatabase.get_current_engine()
        await DatabaseCleanup.full_cleanup(engine)
