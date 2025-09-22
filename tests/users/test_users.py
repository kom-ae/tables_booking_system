from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from tests.users.conftest import (
    EMAIL_ONE,
    USERNAME_ONE,
    USER_UPDATED_ONE,
    VALID_PASSWORD,
    user_crud,
)

from src.core.user import current_admin, current_user
from src.main import app
from src.models.user import User
from src.schemas.user import UserCreate, UserUpdate


@asynccontextmanager
async def override_dependency(
    dep: Any,
    value: Any,
) -> AsyncGenerator[Any, None]:
    """Временное переопределение зависимости FastAPI для тестов."""
    app.dependency_overrides[dep] = lambda: value
    try:
        yield
    finally:
        app.dependency_overrides.pop(dep, None)


@pytest.mark.asyncio
async def test_create_user(session_fixture: AsyncSession) -> None:
    """Тест создания пользователя через CRUD."""
    user_in = UserCreate(
        username=USERNAME_ONE,
        email=EMAIL_ONE,
        phone='+70000000001',
        password=VALID_PASSWORD,
    )
    new_user = await user_crud.create(obj_in=user_in, session=session_fixture)
    assert new_user.id is not None
    assert new_user.username == USERNAME_ONE
    assert new_user.email == EMAIL_ONE


@pytest.mark.asyncio
async def test_update_user(
    session_fixture: AsyncSession,
    normal_user: User,
) -> None:
    """Тест обновления пользователя через CRUD."""
    update_data = UserUpdate(
        username=USER_UPDATED_ONE,
        password=VALID_PASSWORD,
    )
    updated_user = await user_crud.update(
        db_obj=normal_user,
        obj_in=update_data,
        session=session_fixture,
        user_id=normal_user.id,
    )
    assert updated_user.username == USER_UPDATED_ONE
    assert updated_user.password != VALID_PASSWORD  # хэшированный пароль


@pytest.mark.asyncio
async def test_get_users_list(
    session_fixture: AsyncSession,
    admin_user: User,
) -> None:
    """Тест получения списка пользователей через CRUD."""
    users = await user_crud.get_users(
        session=session_fixture,
        show_all=True,
        current_user=admin_user,
    )
    assert len(users) >= 1
    assert any(u.username == 'admin' for u in users)


@pytest.mark.asyncio
async def test_get_current_user(
    client_fixture: AsyncClient,
    normal_user: User,
) -> None:
    """Тест получения текущего пользователя через эндпоинт."""
    async with override_dependency(current_user, normal_user):
        response = await client_fixture.get('/users/me')

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['username'] == normal_user.username
    assert data['email'] == normal_user.email


@pytest.mark.asyncio
async def test_update_current_user_password(
    client_fixture: AsyncClient,
    normal_user: User,
) -> None:
    """Тест обновления пароля текущего пользователя через эндпоинт."""
    async with override_dependency(current_user, normal_user):
        payload = {'username': USER_UPDATED_ONE, 'password': VALID_PASSWORD}
        response = await client_fixture.patch('/users/me', json=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['username'] == USER_UPDATED_ONE


@pytest.mark.asyncio
async def test_get_users_endpoint(
    client_fixture: AsyncClient,
    admin_user: User,
) -> None:
    """Тест получения всех пользователей через эндпоинт."""
    async with override_dependency(current_admin, admin_user):
        response = await client_fixture.get('/users?show_all=true')

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert any(u['username'] == admin_user.username for u in data)
