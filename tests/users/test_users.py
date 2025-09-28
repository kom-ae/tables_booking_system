import asyncio
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

from src.core.dependencies import current_admin, current_user
from src.exceptions.user import (
    UserNotFoundException,
)
from src.main import app
from src.models.user import User
from src.schemas.users import UserCreate, UserUpdate


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


# -------------------
# CRUD: создание
# -------------------
@pytest.mark.asyncio
async def test_create_user(session_fixture: AsyncSession) -> None:
    """Проверка создания нового пользователя."""
    user_in: UserCreate = UserCreate(
        username=USERNAME_ONE,
        email=EMAIL_ONE,
        phone='+70000000001',
        password=VALID_PASSWORD,
    )
    new_user: User = await user_crud.create(
        obj_in=user_in,
        session=session_fixture,
    )
    assert new_user.id is not None
    assert new_user.username == USERNAME_ONE
    assert new_user.email == EMAIL_ONE


@pytest.mark.skip(reason="UserAlreadyExistsException не реализован")
async def test_create_user_duplicate(
    session_fixture: AsyncSession,
    normal_user: User,
) -> None:
    """Проверка UserAlreadyExistsException при создании дубликата."""
    user_in: UserCreate = UserCreate(
        username='duplicate_user',
        email=normal_user.email,
        phone='+70000000002',
        password=VALID_PASSWORD,
    )
    with pytest.raises(UserAlreadyExistsException):
        await user_crud.create(obj_in=user_in, session=session_fixture)


# -------------------
# CRUD: обновление
# -------------------
@pytest.mark.asyncio
async def test_update_user(
    session_fixture: AsyncSession,
    normal_user: User,
) -> None:
    """Проверка обновления данных пользователя."""
    update_data: UserUpdate = UserUpdate(
        username=USER_UPDATED_ONE,
        password=VALID_PASSWORD,
    )
    updated_user: User = await user_crud.update(
        db_obj=normal_user,
        obj_in=update_data,
        session=session_fixture,
        user=normal_user,
    )
    assert updated_user.username == USER_UPDATED_ONE
    assert updated_user.password != VALID_PASSWORD


@pytest.mark.skip(reason="UserAlreadyExistsException не реализован")
async def test_update_user_duplicate(
    session_fixture: AsyncSession,
    normal_user: User,
    another_user: User,
) -> None:
    """Проверка UserAlreadyExistsException при обновлении email."""
    update_data: UserUpdate = UserUpdate(email=normal_user.email)
    with pytest.raises(UserAlreadyExistsException):
        await user_crud.update(
            db_obj=another_user,
            obj_in=update_data,
            session=session_fixture,
        )


# -------------------
# CRUD: получение
# -------------------
@pytest.mark.asyncio
async def test_get_by_name(
    session_fixture: AsyncSession,
    normal_user: User,
) -> None:
    """Проверка получения пользователя по email и телефону."""
    user_by_email: User = await user_crud.get_by_name(
        session_fixture,
        normal_user.email,
    )
    assert user_by_email.id == normal_user.id

    user_by_phone: User = await user_crud.get_by_name(
        session_fixture,
        normal_user.phone,
    )
    assert user_by_phone.id == normal_user.id


@pytest.mark.asyncio
async def test_get_or_404(
    session_fixture: AsyncSession,
    normal_user: User,
) -> None:
    """Проверка get_user_id_or_404: существующий и несуществующий ID."""
    user: User = await user_crud.get_user_id_or_404(
        normal_user.id,
        session_fixture,
    )
    assert user.id == normal_user.id

    with pytest.raises(UserNotFoundException):
        await user_crud.get_user_id_or_404(999999, session_fixture)


# -------------------
# CRUD: last_used
# -------------------
@pytest.mark.asyncio
async def test_update_last_used(
    session_fixture: AsyncSession,
    normal_user: User,
) -> None:
    """Проверка обновления поля last_used пользователя."""
    last_used_before = normal_user.last_used
    await asyncio.sleep(0.1)
    updated_user: User = await user_crud.update_last_used(
        session_fixture,
        normal_user,
    )
    assert updated_user.last_used >= last_used_before


@pytest.mark.asyncio
async def test_touch_last_used(
    session_fixture: AsyncSession,
    normal_user: User,
) -> None:
    """Проверка метода touch_last_used: должно выполняться без ошибок."""
    await user_crud.update_last_used(session_fixture, normal_user)


# -------------------
# Эндпоинты: /me
# -------------------
@pytest.mark.asyncio
async def test_get_current_user(
    client_fixture: AsyncClient,
    normal_user: User,
) -> None:
    """Проверка получения данных текущего пользователя."""
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
    """Проверка обновления пароля текущего пользователя."""
    async with override_dependency(current_user, normal_user):
        payload = {'username': USER_UPDATED_ONE, 'password': VALID_PASSWORD}
        response = await client_fixture.patch('/users/me', json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['username'] == USER_UPDATED_ONE


# -------------------
# Эндпоинты: /users (админ)
# -------------------
@pytest.mark.asyncio
async def test_get_users_endpoint(
    client_fixture: AsyncClient,
    admin_user: User,
) -> None:
    """Проверка получения списка пользователей админом."""
    async with override_dependency(current_admin, admin_user):
        response = await client_fixture.get('/users?show_all=true')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert any(user['username'] == admin_user.username for user in data)


@pytest.mark.asyncio
async def test_get_user_by_id_endpoint(
    client_fixture: AsyncClient,
    admin_user: User,
    normal_user: User,
) -> None:
    """Проверка получения пользователя по ID админом."""
    async with override_dependency(current_admin, admin_user):
        response = await client_fixture.get(f'/users/{normal_user.id}')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['id'] == normal_user.id


@pytest.mark.asyncio
async def test_update_user_by_id_endpoint(
    client_fixture: AsyncClient,
    admin_user: User,
    normal_user: User,
) -> None:
    """Проверка обновления пользователя по ID админом."""
    async with override_dependency(current_admin, admin_user):
        payload = {'username': USER_UPDATED_ONE, 'password': VALID_PASSWORD}
        response = await client_fixture.patch(
            f'/users/{normal_user.id}',
            json=payload,
        )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['username'] == USER_UPDATED_ONE


# -------------------
# Эндпоинты: ошибки
# -------------------
@pytest.mark.asyncio
async def test_get_current_user_without_auth(
    client_fixture: AsyncClient,
) -> None:
    """Проверка запроса /me без авторизации."""
    response = await client_fixture.get('/users/me')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_update_current_user_invalid_data(
    client_fixture: AsyncClient,
    normal_user: User,
) -> None:
    """Проверка обновления пользователя с некорректными данными."""
    async with override_dependency(current_user, normal_user):
        payload = {'email': 'invalid-email'}
        response = await client_fixture.patch('/users/me', json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# -------------------
# Эндпоинты: дополнительные проверки
# -------------------
@pytest.mark.asyncio
async def test_get_users_only_active(
    client_fixture: AsyncClient,
    admin_user: User,
    normal_user: User,
    session_fixture: AsyncSession,
) -> None:
    """Проверка, что show_all=False возвращает только активных юзеров."""
    # деактивируем normal_user
    normal_user.is_active = False
    session_fixture.add(normal_user)
    await session_fixture.commit()

    async with override_dependency(current_admin, admin_user):
        response = await client_fixture.get('/users?show_all=false')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(user['is_active'] for user in data)
    assert normal_user.username not in [user['username'] for user in data]


@pytest.mark.asyncio
async def test_create_user_duplicate_endpoint(
    client_fixture: AsyncClient,
    normal_user: User,
) -> None:
    """Проверка, что дубликат email/phone через POST /users вызывает ошибку."""
    payload: dict = {
        'username': 'newuser',
        'email': normal_user.email,
        'phone': '+70000000003',
        'password': VALID_PASSWORD,
    }
    response = await client_fixture.post('/users', json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data['error'] == 'DBIntegrityError'


@pytest.mark.asyncio
async def test_get_me_security(
    client_fixture: AsyncClient,
    normal_user: User,
    another_user: User,
) -> None:
    """Проверка, что другой пользователь не может получить чужие данные."""
    async with override_dependency(current_user, another_user):
        response = await client_fixture.get('/users/me')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data['username'] == another_user.username
