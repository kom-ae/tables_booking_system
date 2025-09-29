"""Базовые фикстуры и конфигурация для тестов API системы бронирования столов.

Этот модуль содержит общие фикстуры, константы и утилиты для всех тестов.
"""

from typing import Any, AsyncGenerator, Dict

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.core.db import engine, get_async_session
from src.crud.factory import get_cafe_crud
from src.main import app
from src.models.base import BaseModel
from src.models.cafe import Cafe
from src.models.user import User
from src.schemas.auth import Auth
from src.schemas.cafes import CafeCreate
from src.services.auth import PasswordService

# -----------------------
# Константы для эндпоинтов
# -----------------------

# Базовые эндпоинты
ENDPOINTS = {
    'auth': {
        'login': '/auth/login',
        'register': '/auth/register',
        'refresh': '/auth/refresh',
    },
    'users': {
        'list': '/users',
        'create': '/users',
        'get': '/users/{user_id}',
        'update': '/users/{user_id}',
        'delete': '/users/{user_id}',
    },
    'cafes': {
        'list': '/cafes',
        'create': '/cafes',
        'get': '/cafes/{cafe_id}',
        'update': '/cafes/{cafe_id}',
    },
    # Нереализованные эндпоинты (для будущего использования)
    'actions': {
        'list': '/actions',
        'create': '/actions',
        'get': '/actions/{action_id}',
        'update': '/actions/{action_id}',
    },
    'bookings': {
        'list': '/booking',
        'create': '/booking',
        'get': '/booking/{booking_id}',
        'update': '/booking/{booking_id}',
    },
    'dishes': {
        'list': '/dishes',
        'create': '/dishes',
        'get': '/dishes/{dish_id}',
        'update': '/dishes/{dish_id}',
    },
    'tables': {
        'list': '/cafe/{cafe_id}/tables',
        'create': '/cafe/{cafe_id}/tables',
        'get': '/cafe/{cafe_id}/tables/{table_id}',
        'update': '/cafe/{cafe_id}/tables/{table_id}',
    },
    'time_slots': {
        'list': '/cafe/{cafe_id}/time_slots',
        'create': '/cafe/{cafe_id}/time_slots',
        'get': '/cafe/{cafe_id}/time_slots/{slot_id}',
        'update': '/cafe/{cafe_id}/time_slots/{slot_id}',
    },
}

# Валидные данные для тестов
VALID_PASSWORD = 'Vx9!rT#4qLp$2mZ'
VALID_PHONE = '+70000000001'
VALID_EMAIL = 'test@example.com'
VALID_USERNAME = 'testuser'
VALID_CAFE_NAME = 'Test Cafe'
VALID_CAFE_ADDRESS = 'Test Address 123'
VALID_CAFE_PHONE = '+70000000002'

# Тестовые данные пользователей
TEST_USERS: Dict[str, Dict[str, Any]] = {
    'admin': {
        'username': 'admin',
        'email': 'admin@test.com',
        'phone': '+70000000001',
        'password': VALID_PASSWORD,
        'role': 'admin',
        'tg_id': None,
    },
    'manager': {
        'username': 'manager',
        'email': 'manager@test.com',
        'phone': '+70000000002',
        'password': VALID_PASSWORD,
        'role': 'manager',
        'tg_id': None,
    },
    'user': {
        'username': 'user',
        'email': 'user@test.com',
        'phone': '+70000000003',
        'password': VALID_PASSWORD,
        'role': 'user',
        'tg_id': None,
    },
    'user2': {
        'username': 'user2',
        'email': 'user2@test.com',
        'phone': '+70000000004',
        'password': VALID_PASSWORD,
        'role': 'user',
        'tg_id': None,
    },
}

# Тестовые данные кафе
TEST_CAFES: Dict[str, Dict[str, str]] = {
    'cafe1': {
        'name': 'Cafe One',
        'address': 'Address One 123',
        'phone': '+70000000010',
        'description': 'First test cafe',
    },
    'cafe2': {
        'name': 'Cafe Two',
        'address': 'Address Two 456',
        'phone': '+70000000011',
        'description': 'Second test cafe',
    },
}

# Невалидные данные для тестов валидации
INVALID_DATA = {
    'invalid_email': 'not-an-email',
    'invalid_phone': '123',
    'short_password': '123',
    'empty_username': '',
    'long_username': 'x' * 300,
    'invalid_phone_format': '123456789',
}

# -----------------------
# Базовые фикстуры
# -----------------------


@pytest_asyncio.fixture
async def session_fixture() -> AsyncGenerator[AsyncSession, None]:
    """Асинхронная сессия для тестов."""
    async for session in get_async_session():
        try:
            yield session
        except Exception:
            # Если произошла ошибка, откатываем транзакцию
            await session.rollback()
            raise
        finally:
            # Закрываем сессию
            await session.close()


@pytest_asyncio.fixture(autouse=True)
async def init_database(session_fixture: AsyncSession) -> None:
    """Инициализация базы данных перед каждым тестом."""
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)


@pytest_asyncio.fixture(autouse=True)
async def cleanup_db(
    session_fixture: AsyncSession,
) -> AsyncGenerator[None, None]:
    """Очищаем все таблицы перед каждым тестом."""
    # Очищаем в правильном порядке из-за внешних ключей
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

    # Очистка перед тестом
    try:
        # Откатываем любые незавершенные транзакции
        await session_fixture.rollback()

        for table in tables_to_clean:
            try:
                await session_fixture.execute(text(f'DELETE FROM {table};'))
            except Exception:
                # Игнорируем ошибки для несуществующих таблиц
                pass

        await session_fixture.commit()
    except Exception:
        # Если произошла ошибка, откатываем транзакцию
        try:
            await session_fixture.rollback()
        except Exception:
            pass

    # Очистка после теста
    yield

    try:
        # Откатываем любые незавершенные транзакции
        await session_fixture.rollback()

        for table in tables_to_clean:
            try:
                await session_fixture.execute(text(f'DELETE FROM {table};'))
            except Exception:
                # Игнорируем ошибки для несуществующих таблиц
                pass

        await session_fixture.commit()
    except Exception:
        # Если произошла ошибка, откатываем транзакцию
        try:
            await session_fixture.rollback()
        except Exception:
            pass


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
# Фикстуры пользователей
# -----------------------


@pytest_asyncio.fixture
async def admin_user(session_fixture: AsyncSession) -> User:
    """Создаём администратора для тестов."""
    admin_data = TEST_USERS['admin']
    user = User(
        username=admin_data['username'],
        email=admin_data['email'],
        phone=admin_data['phone'],
        password=PasswordService.hash_password(admin_data['password']),
        role=admin_data['role'],
        tg_id=admin_data.get('tg_id'),
    )
    session_fixture.add(user)
    await session_fixture.commit()
    await session_fixture.refresh(user)
    return user


@pytest_asyncio.fixture
async def manager_user(session_fixture: AsyncSession) -> User:
    """Создаём менеджера для тестов."""
    manager_data = TEST_USERS['manager']
    user = User(
        username=manager_data['username'],
        email=manager_data['email'],
        phone=manager_data['phone'],
        password=PasswordService.hash_password(manager_data['password']),
        role=manager_data['role'],
        tg_id=manager_data.get('tg_id'),
    )
    session_fixture.add(user)
    await session_fixture.commit()
    await session_fixture.refresh(user)
    return user


@pytest_asyncio.fixture
async def normal_user(session_fixture: AsyncSession) -> User:
    """Создаём обычного пользователя для тестов."""
    user_data = TEST_USERS['user']
    user = User(
        username=user_data['username'],
        email=user_data['email'],
        phone=user_data['phone'],
        password=PasswordService.hash_password(user_data['password']),
        role=user_data['role'],
        tg_id=user_data.get('tg_id'),
    )
    session_fixture.add(user)
    await session_fixture.commit()
    await session_fixture.refresh(user)
    return user


@pytest_asyncio.fixture
async def another_user(session_fixture: AsyncSession) -> User:
    """Создаём второго пользователя для тестов."""
    user_data = TEST_USERS['user2']
    user = User(
        username=user_data['username'],
        email=user_data['email'],
        phone=user_data['phone'],
        password=PasswordService.hash_password(user_data['password']),
        role=user_data['role'],
        tg_id=user_data.get('tg_id'),
    )
    session_fixture.add(user)
    await session_fixture.commit()
    await session_fixture.refresh(user)
    return user


# -----------------------
# Фикстуры кафе
# -----------------------


@pytest_asyncio.fixture
async def test_cafe(session_fixture: AsyncSession) -> Cafe:
    """Создаём тестовое кафе."""
    cafe_data = dict(TEST_CAFES['cafe1'])
    cafe_in = CafeCreate(
        name=cafe_data['name'],
        address=cafe_data['address'],
        phone=cafe_data['phone'],
        description=cafe_data['description'],
        photo='',
        managers=[],
    )
    cafe_db = await get_cafe_crud().create_cafe(cafe_in, session_fixture)
    # Возвращаем объект модели из БД
    cafe = await session_fixture.get(Cafe, cafe_db.id)
    assert cafe is not None
    return cafe


@pytest_asyncio.fixture
async def test_cafe2(session_fixture: AsyncSession) -> Cafe:
    """Создаём второе тестовое кафе."""
    cafe_data = dict(TEST_CAFES['cafe2'])
    cafe_in = CafeCreate(
        name=cafe_data['name'],
        address=cafe_data['address'],
        phone=cafe_data['phone'],
        description=cafe_data['description'],
        photo='',
        managers=[],
    )
    cafe_db = await get_cafe_crud().create_cafe(cafe_in, session_fixture)
    # Возвращаем объект модели из БД
    cafe = await session_fixture.get(Cafe, cafe_db.id)
    assert cafe is not None
    return cafe


# -----------------------
# Фикстуры аутентификации
# -----------------------


@pytest_asyncio.fixture
async def admin_token(
    client_fixture: AsyncClient,
    admin_user: User,
) -> str:
    """Возвращает токен авторизации администратора."""
    payload = Auth(
        name=admin_user.email,
        password=VALID_PASSWORD,
    ).model_dump()
    response = await client_fixture.post('/auth/login', json=payload)
    assert response.status_code == status.HTTP_200_OK
    return response.json()['token']


@pytest_asyncio.fixture
async def manager_token(
    client_fixture: AsyncClient,
    manager_user: User,
) -> str:
    """Возвращает токен авторизации менеджера."""
    payload = Auth(
        name=manager_user.email,
        password=VALID_PASSWORD,
    ).model_dump()
    response = await client_fixture.post('/auth/login', json=payload)
    assert response.status_code == status.HTTP_200_OK
    return response.json()['token']


@pytest_asyncio.fixture
async def user_token(
    client_fixture: AsyncClient,
    normal_user: User,
) -> str:
    """Возвращает токен авторизации обычного пользователя."""
    payload = Auth(
        name=normal_user.email,
        password=VALID_PASSWORD,
    ).model_dump()
    response = await client_fixture.post('/auth/login', json=payload)
    assert response.status_code == status.HTTP_200_OK
    return response.json()['token']


# -----------------------
# Утилиты для тестов
# -----------------------


def get_auth_headers(token: str) -> Dict[str, str]:
    """Возвращает заголовки авторизации для запросов."""
    return {'Authorization': f'Bearer {token}'}


def assert_error_response(
    response: Any,
    expected_status: int,
    expected_message: str | None = None,
) -> None:
    """Проверяет ответ с ошибкой."""
    assert response.status_code == expected_status
    if expected_message:
        data = response.json()
        assert 'message' in data or 'error' in data


def assert_success_response(
    response: Any,
    expected_status: int = status.HTTP_200_OK,
) -> None:
    """Проверяет успешный ответ."""
    assert response.status_code == expected_status
    assert response.json() is not None


def get_endpoint_url(endpoint_type: str, action: str, **kwargs) -> str:
    """Возвращает URL эндпоинта с подстановкой параметров."""
    endpoint = ENDPOINTS[endpoint_type][action]
    return endpoint.format(**kwargs)


def get_cafe_endpoint_url(action: str, cafe_id: int, **kwargs) -> str:
    """Возвращает URL эндпоинта кафе с подстановкой параметров."""
    endpoint = ENDPOINTS['cafes'][action]
    return endpoint.format(cafe_id=cafe_id, **kwargs)


def get_user_endpoint_url(action: str, user_id: int, **kwargs) -> str:
    """Возвращает URL эндпоинта пользователя с подстановкой параметров."""
    endpoint = ENDPOINTS['users'][action]
    return endpoint.format(user_id=user_id, **kwargs)


# -----------------------
# Фикстуры для будущих компонентов
# -----------------------

# Эти фикстуры будут использоваться когда компоненты будут реализованы


@pytest_asyncio.fixture
async def test_table(session_fixture: AsyncSession, test_cafe: Cafe) -> None:
    """Фикстура для тестового стола (когда будет реализовано)."""
    # TODO: Реализовать когда модель Table будет готова
    pass


@pytest_asyncio.fixture
async def test_time_slot(
    session_fixture: AsyncSession,
    test_cafe: Cafe,
) -> None:
    """Фикстура для тестового временного слота (когда будет реализовано)."""
    # TODO: Реализовать когда модель TimeSlot будет готова
    pass


@pytest_asyncio.fixture
async def test_action(session_fixture: AsyncSession, test_cafe: Cafe) -> None:
    """Фикстура для тестовой акции (когда будет реализовано)."""
    # TODO: Реализовать когда модель Action будет готова
    pass


@pytest_asyncio.fixture
async def test_booking(
    session_fixture: AsyncSession,
    normal_user: User,
    test_cafe: Cafe,
) -> None:
    """Фикстура для тестового бронирования (когда будет реализовано)."""
    # TODO: Реализовать когда модель Booking будет готова
    pass


@pytest_asyncio.fixture
async def test_dish(session_fixture: AsyncSession, test_cafe: Cafe) -> None:
    """Фикстура для тестового блюда (когда будет реализовано)."""
    # TODO: Реализовать когда модель Dish будет готова
    pass
