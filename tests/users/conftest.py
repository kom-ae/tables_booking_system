from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.db import get_async_session
from src.crud.factory import get_user_crud
from src.main import app
from src.models.user import User
from src.schemas.auth import Auth
from src.schemas.users import UserCreate

user_crud = get_user_crud()


VALID_PASSWORD = 'Vx9!rT#4qLp$2mZ'
PHONE_ONE = '+70000000001'
PHONE_TWO = '+70000000002'
PHONE_THREE = '+70000000003'
USERNAME_ONE = 'user1'
USERNAME_TWO = 'user2'
USERNAME_THREE = 'user3'
EMAIL_ONE = 'user1@test.com'
EMAIL_TWO = 'user2@test.com'
EMAIL_THREE = 'user3@test.com'
USER_UPDATED_ONE = 'user_updated'


# -----------------------
# Сессия и очистка БД
# -----------------------
@pytest_asyncio.fixture
async def session_fixture() -> AsyncGenerator[AsyncSession, None]:
    """Асинхронная сессия для тестов."""
    async for session in get_async_session():
        yield session


@pytest_asyncio.fixture(autouse=True)
async def cleanup_db(session_fixture: AsyncSession) -> None:
    """Очищаем таблицу пользователей перед каждым тестом."""
    await session_fixture.execute(text('DELETE FROM user;'))
    await session_fixture.commit()


# -----------------------
# Клиент
# -----------------------
@pytest_asyncio.fixture
async def client_fixture(
    session_fixture: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """AsyncClient для тестирования эндпоинтов FastAPI."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url='http://testserver',
    ) as client:
        app.dependency_overrides[get_async_session] = lambda: session_fixture
        yield client
        app.dependency_overrides.clear()


# -----------------------
# Пользователи
# -----------------------
@pytest_asyncio.fixture
async def normal_user(session_fixture: AsyncSession) -> User:
    """Создаём обычного пользователя для тестов."""
    user_in = UserCreate(
        username=USERNAME_ONE,
        email=EMAIL_ONE,
        password=VALID_PASSWORD,
        phone=PHONE_ONE,
    )
    return await user_crud.create(obj_in=user_in, session=session_fixture)


@pytest_asyncio.fixture
async def another_user(session_fixture: AsyncSession) -> User:
    """Создаём второго пользователя для тестов дубликатов."""
    user_in = UserCreate(
        username=USERNAME_TWO,
        email=EMAIL_TWO,
        password=VALID_PASSWORD,
        phone=PHONE_TWO,
    )
    return await user_crud.create(obj_in=user_in, session=session_fixture)


@pytest_asyncio.fixture
async def admin_user(session_fixture: AsyncSession) -> User:
    """Создаём администратора для тестов."""
    user_in = UserCreate(
        username='admin',
        email='admin@test.com',
        password=VALID_PASSWORD,
        phone='+70000000004',
        is_admin=True,
    )
    return await user_crud.create(obj_in=user_in, session=session_fixture)


# -----------------------
# Фикстуры для аутентификации
# -----------------------
@pytest_asyncio.fixture
async def auth_token_email(
    client_fixture: AsyncClient,
    normal_user: User,
) -> str:
    """Возвращает токен авторизации по email."""
    payload = Auth(
        name=normal_user.email,
        password=VALID_PASSWORD,
    ).model_dump()
    response = await client_fixture.post('/auth/login', json=payload)
    assert response.status_code == status.HTTP_200_OK
    return response.json()['token']


@pytest_asyncio.fixture
async def auth_token_phone(
    client_fixture: AsyncClient,
    normal_user: User,
) -> str:
    """Возвращает токен авторизации по телефону."""
    payload = Auth(
        name=normal_user.phone,
        password=VALID_PASSWORD,
    ).model_dump()
    response = await client_fixture.post('/auth/login', json=payload)
    assert response.status_code == status.HTTP_200_OK
    return response.json()['token']
