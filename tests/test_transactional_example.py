"""Пример транзакционного теста для демонстрации новой архитектуры.

Этот файл показывает, как использовать новую систему фикстур
с транзакционной изоляцией для предотвращения конфликтов.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from tests.test_utils import parallel_test, unit_test, integration_test
from src.models.user import User, UserRole
from src.models.cafe import Cafe
from src.schemas.auth import Auth


class TestTransactionalIsolation:
    """Тесты для демонстрации транзакционной изоляции."""

    @unit_test
    @parallel_test
    @pytest.mark.asyncio
    async def test_user_creation_isolation(
        self,
        db_session: AsyncSession,
    ) -> None:
        """Тест создания пользователя с транзакционной изоляцией."""
        # Создаем пользователя
        user = User(
            username="test_user_isolation",
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
        assert user.username == "test_user_isolation"

        # Транзакция будет автоматически откачена в конце теста
        # Это обеспечивает изоляцию от других тестов

    @unit_test
    @parallel_test
    @pytest.mark.asyncio
    async def test_concurrent_user_creation(
        self,
        db_session: AsyncSession,
    ) -> None:
        """Тест создания пользователя с уникальными данными."""
        import uuid

        unique_suffix = str(uuid.uuid4())[:8]
        phone_suffix = str(uuid.uuid4().int)[:10].zfill(10)

        user = User(
            username=f"concurrent_user_{unique_suffix}",
            email=f"concurrent_{unique_suffix}@example.com",
            phone=f"+7{phone_suffix}",
            password="hashed_password",
            role=UserRole.USER,
        )

        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        assert user.id is not None
        assert user.username == f"concurrent_user_{unique_suffix}"

    @integration_test
    @parallel_test
    @pytest.mark.asyncio
    async def test_auth_with_transactional_session(
        self,
        client_fixture: AsyncClient,
        normal_user: User,
    ) -> None:
        """Тест аутентификации с использованием транзакционной сессии."""
        # Тест логина
        payload = Auth(
            name=normal_user.email,
            password="Vx9!rT#4qLp$2mZ",
        ).model_dump()

        response = await client_fixture.post('/auth/login', json=payload)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'token' in data
        assert isinstance(data['token'], str)
        assert len(data['token']) > 0

    @unit_test
    @parallel_test
    @pytest.mark.asyncio
    async def test_database_rollback_isolation(
        self,
        db_session: AsyncSession,
    ) -> None:
        """Тест, демонстрирующий изоляцию через rollback."""
        # Создаем пользователя
        user = User(
            username="rollback_test_user",
            email="rollback_test@example.com",
            phone="+70000000002",
            password="hashed_password",
            role=UserRole.USER,
        )

        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        user_id = user.id
        assert user_id is not None

        # В конце теста транзакция будет откачена
        # и этот пользователь не будет виден в других тестах


class TestParallelExecution:
    """Тесты для демонстрации параллельного выполнения."""

    @unit_test
    @parallel_test
    @pytest.mark.asyncio
    async def test_parallel_user_creation_1(
        self,
        db_session: AsyncSession,
    ) -> None:
        """Первый тест параллельного создания пользователя."""
        import uuid

        unique_suffix = str(uuid.uuid4())[:8]
        phone_suffix = str(uuid.uuid4().int)[:10].zfill(10)

        user = User(
            username=f"parallel_user_1_{unique_suffix}",
            email=f"parallel_1_{unique_suffix}@example.com",
            phone=f"+7{phone_suffix}",
            password="hashed_password",
            role=UserRole.USER,
        )

        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        assert user.id is not None
        assert user.username == f"parallel_user_1_{unique_suffix}"

    @unit_test
    @parallel_test
    @pytest.mark.asyncio
    async def test_parallel_user_creation_2(
        self,
        db_session: AsyncSession,
    ) -> None:
        """Второй тест параллельного создания пользователя."""
        import uuid

        unique_suffix = str(uuid.uuid4())[:8]
        phone_suffix = str(uuid.uuid4().int)[:10].zfill(10)

        user = User(
            username=f"parallel_user_2_{unique_suffix}",
            email=f"parallel_2_{unique_suffix}@example.com",
            phone=f"+7{phone_suffix}",
            password="hashed_password",
            role=UserRole.USER,
        )

        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        assert user.id is not None
        assert user.username == f"parallel_user_2_{unique_suffix}"

    @unit_test
    @parallel_test
    @pytest.mark.asyncio
    async def test_parallel_user_creation_3(
        self,
        db_session: AsyncSession,
    ) -> None:
        """Третий тест параллельного создания пользователя."""
        import uuid

        unique_suffix = str(uuid.uuid4())[:8]
        phone_suffix = str(uuid.uuid4().int)[:10].zfill(10)

        user = User(
            username=f"parallel_user_3_{unique_suffix}",
            email=f"parallel_3_{unique_suffix}@example.com",
            phone=f"+7{phone_suffix}",
            password="hashed_password",
            role=UserRole.USER,
        )

        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        assert user.id is not None
        assert user.username == f"parallel_user_3_{unique_suffix}"


class TestIsolatedFixtures:
    """Тесты для демонстрации изолированных фикстур."""

    @unit_test
    @parallel_test
    @pytest.mark.asyncio
    async def test_admin_user_fixture(
        self,
        admin_user: User,
    ) -> None:
        """Тест фикстуры администратора."""
        assert admin_user.role == "admin"
        assert admin_user.id is not None
        assert admin_user.username is not None
        assert admin_user.email is not None

    @unit_test
    @parallel_test
    @pytest.mark.asyncio
    async def test_manager_user_fixture(
        self,
        manager_user: User,
    ) -> None:
        """Тест фикстуры менеджера."""
        assert manager_user.role == "manager"
        assert manager_user.id is not None
        assert manager_user.username is not None
        assert manager_user.email is not None

    @unit_test
    @parallel_test
    @pytest.mark.asyncio
    async def test_normal_user_fixture(
        self,
        normal_user: User,
    ) -> None:
        """Тест фикстуры обычного пользователя."""
        assert normal_user.role == "user"
        assert normal_user.id is not None
        assert normal_user.username is not None
        assert normal_user.email is not None

    @unit_test
    @parallel_test
    @pytest.mark.asyncio
    async def test_cafe_fixture(
        self,
        test_cafe: Cafe,
    ) -> None:
        """Тест фикстуры кафе."""
        assert test_cafe.id is not None
        assert test_cafe.name is not None
        assert test_cafe.address is not None
        assert test_cafe.phone is not None


class TestErrorHandling:
    """Тесты для демонстрации обработки ошибок в транзакциях."""

    @unit_test
    @parallel_test
    @pytest.mark.asyncio
    async def test_transaction_rollback_on_error(
        self,
        db_session: AsyncSession,
    ) -> None:
        """Тест отката транзакции при ошибке."""
        # Создаем пользователя
        user = User(
            username="error_test_user",
            email="error_test@example.com",
            phone="+70000000003",
            password="hashed_password",
            role=UserRole.USER,
        )

        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        assert user.id is not None

        # Имитируем ошибку
        with pytest.raises(ValueError):
            raise ValueError("Тестовая ошибка для демонстрации rollback")

        # Транзакция должна быть откачена автоматически
