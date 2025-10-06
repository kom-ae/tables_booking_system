"""Тест для проверки новой архитектуры фикстур.

Этот файл содержит простые тесты для проверки работы
транзакционной изоляции и параллельного выполнения.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.test_utils import parallel_test, unit_test, integration_test
from src.models.user import User, UserRole


class TestNewArchitecture:
    """Тесты для проверки новой архитектуры фикстур."""

    @unit_test
    @parallel_test
    @pytest.mark.asyncio
    async def test_transactional_isolation(
        self,
        db_session: AsyncSession,
    ) -> None:
        """Тест транзакционной изоляции."""
        # Создаем пользователя
        user = User(
            username="test_isolation_user",
            email="test_isolation@example.com",
            phone="+70000000001",
            password="hashed_password",
            role=UserRole.USER,
        )

        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        # Проверяем, что пользователь создан
        assert user.id is not None
        assert user.username == "test_isolation_user"

        # Транзакция будет автоматически откачена в конце теста

    @unit_test
    @parallel_test
    @pytest.mark.asyncio
    async def test_unique_data_generation(
        self,
        db_session: AsyncSession,
    ) -> None:
        """Тест генерации уникальных данных."""
        import uuid

        unique_suffix = str(uuid.uuid4())[:8]
        phone_suffix = str(uuid.uuid4().int)[:10].zfill(10)

        user = User(
            username=f"unique_user_{unique_suffix}",
            email=f"unique_{unique_suffix}@example.com",
            phone=f"+7{phone_suffix}",
            password="hashed_password",
            role=UserRole.USER,
        )

        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        assert user.id is not None
        assert user.username == f"unique_user_{unique_suffix}"

    @integration_test
    @parallel_test
    @pytest.mark.asyncio
    async def test_fixture_isolation(
        self,
        admin_user: User,
        normal_user: User,
    ) -> None:
        """Тест изоляции фикстур."""
        # Проверяем, что фикстуры создают разных пользователей
        assert admin_user.id != normal_user.id
        assert admin_user.role == "admin"
        assert normal_user.role == "user"
        assert admin_user.email != normal_user.email

    @unit_test
    @parallel_test
    @pytest.mark.asyncio
    async def test_parallel_execution_safety(
        self,
        db_session: AsyncSession,
    ) -> None:
        """Тест безопасности параллельного выполнения."""
        import uuid

        unique_suffix = str(uuid.uuid4())[:8]

        # Создаем несколько пользователей
        users = []
        for i in range(3):
            phone_suffix = str(uuid.uuid4().int)[:10].zfill(10)
            user = User(
                username=f"parallel_user_{i}_{unique_suffix}",
                email=f"parallel_{i}_{unique_suffix}@example.com",
                phone=f"+7{phone_suffix}",
                password="hashed_password",
                role=UserRole.USER,
            )
            db_session.add(user)
            users.append(user)

        await db_session.flush()

        # Проверяем, что все пользователи созданы
        for user in users:
            await db_session.refresh(user)
            assert user.id is not None
            assert user.username.startswith("parallel_user_")
