"""Базовые фикстуры и конфигурация для тестов API системы бронирования столов.

Этот модуль содержит общие фикстуры, константы и утилиты для всех тестов.
Использует транзакционную изоляцию для предотвращения конфликтов
при параллельном выполнении.
"""

import uuid
from datetime import date, timedelta
from types import SimpleNamespace
from typing import Any, AsyncGenerator, Dict

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette import status

from src.core.db import engine, get_async_session
from src.crud.action import actions_crud
from src.crud.factory import (
    get_booking_crud,
    get_cafe_crud,
    get_slot_crud,
    get_table_crud)
from src.main import app
from src.models.action import Action
from src.models.base import BaseModel
from src.models.cafe import Cafe
from src.models.dish import Dishe
from src.models.user import User
from src.schemas.action import ActionCreate
from src.schemas.auth import Auth
from src.schemas.cafes import CafeCreate
from src.schemas.slots import SlotCreate
from src.schemas.table import TableCreate
from src.services.auth import PasswordService
from src.schemas.bookings import BookingCreate

# Импортируем тестовую конфигурацию
from tests.database_manager import db_manager, ParallelTestDatabase

# -----------------------
# Тестовый движок базы данных
# -----------------------

# Получаем движок для текущего worker'а
test_engine = db_manager.get_engine()

# Создаем фабрику сессий
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

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

TEST_ACTIONS: Dict[str, Dict[str, Any]] = {
    'action1': {
        'cafe': 1,
        'description': 'Скидка 20% на все бургеры по вторникам',
    }
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
# Базовые фикстуры с транзакционной изоляцией
# -----------------------


@pytest_asyncio.fixture(scope='session')
async def setup_test_db():
    """Настройка тестовой базы данных на уровне сессии."""
    # Убеждаемся, что база данных для текущего worker'а существует
    await ParallelTestDatabase.ensure_database_exists()

    # Создаем все таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)

    yield

    # Очищаем после всех тестов
    async with test_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)

    # Закрываем движок
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session(setup_test_db) -> AsyncGenerator[AsyncSession, None]:
    """Транзакционная сессия базы данных для тестов.

    Каждый тест получает свою собственную транзакцию, которая автоматически
    откатывается в конце теста, обеспечивая полную изоляцию.
    """
    # Создаем новую сессию
    async with TestSessionLocal() as session:
        # Начинаем транзакцию
        transaction = await session.begin()
        try:
            yield session
        except Exception:
            # Если произошла ошибка, откатываем транзакцию
            await transaction.rollback()
            raise
        finally:
            # Всегда откатываем транзакцию в конце теста
            # Это обеспечивает изоляцию между тестами
            await transaction.rollback()
            await session.close()


@pytest_asyncio.fixture
async def client_fixture(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """AsyncClient для тестирования эндпоинтов FastAPI."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url='http://testserver',
    ) as client:
        # Переопределяем зависимость для изолированной сессии
        app.dependency_overrides[get_async_session] = lambda: db_session
        yield client
        app.dependency_overrides.clear()


# -----------------------
# Фикстуры пользователей с уникальными данными
# -----------------------


def _generate_unique_user_data(base_data: Dict[str, Any]) -> Dict[str, Any]:
    """Генерирует уникальные данные пользователя для избежания конфликтов."""
    unique_suffix = str(uuid.uuid4())[:8]
    return {
        **base_data,
        'username': f"{base_data['username']}_{unique_suffix}",
        'email': f"{unique_suffix}_{base_data['email']}",
        'phone': f"+7000000{unique_suffix}",
    }


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Создаём администратора для тестов с уникальными данными."""
    admin_data = _generate_unique_user_data(TEST_USERS['admin'])
    user = User(
        username=admin_data['username'],
        email=admin_data['email'],
        phone=admin_data['phone'],
        password=PasswordService.hash_password(admin_data['password']),
        role=admin_data['role'],
        tg_id=admin_data.get('tg_id'),
    )
    db_session.add(user)
    await db_session.flush()  # flush вместо commit для транзакционной изоляции
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def manager_user(db_session: AsyncSession) -> User:
    """Создаём менеджера для тестов с уникальными данными."""
    manager_data = _generate_unique_user_data(TEST_USERS['manager'])
    user = User(
        username=manager_data['username'],
        email=manager_data['email'],
        phone=manager_data['phone'],
        password=PasswordService.hash_password(manager_data['password']),
        role=manager_data['role'],
        tg_id=manager_data.get('tg_id'),
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def normal_user(db_session: AsyncSession) -> User:
    """Создаём обычного пользователя для тестов с уникальными данными."""
    user_data = _generate_unique_user_data(TEST_USERS['user'])
    user = User(
        username=user_data['username'],
        email=user_data['email'],
        phone=user_data['phone'],
        password=PasswordService.hash_password(user_data['password']),
        role=user_data['role'],
        tg_id=user_data.get('tg_id'),
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def another_user(db_session: AsyncSession) -> User:
    """Создаём второго пользователя для тестов с уникальными данными."""
    user_data = _generate_unique_user_data(TEST_USERS['user2'])
    user = User(
        username=user_data['username'],
        email=user_data['email'],
        phone=user_data['phone'],
        password=PasswordService.hash_password(user_data['password']),
        role=user_data['role'],
        tg_id=user_data.get('tg_id'),
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


# -----------------------
# Фикстуры кафе с уникальными данными
# -----------------------


def _generate_unique_cafe_data(base_data: Dict[str, str]) -> Dict[str, str]:
    """Генерирует уникальные данные кафе для избежания конфликтов."""
    unique_suffix = str(uuid.uuid4())[:8]
    return {
        **base_data,
        'name': f"{base_data['name']} {unique_suffix}",
        'phone': f"+7000000{unique_suffix}",
    }


@pytest_asyncio.fixture
async def test_cafe(db_session: AsyncSession) -> Cafe:
    """Создаём тестовое кафе с уникальными данными."""
    cafe_data = _generate_unique_cafe_data(TEST_CAFES['cafe1'])
    cafe_in = CafeCreate(
        name=cafe_data['name'],
        address=cafe_data['address'],
        phone=cafe_data['phone'],
        description=cafe_data['description'],
        photo='',
        managers=[],
    )
    cafe_db = await get_cafe_crud().create(cafe_in, db_session)
    # Возвращаем объект модели из БД
    cafe = await db_session.get(Cafe, cafe_db.id)
    assert cafe is not None
    return cafe


@pytest_asyncio.fixture
async def test_cafe2(db_session: AsyncSession) -> Cafe:
    """Создаём второе тестовое кафе с уникальными данными."""
    cafe_data = _generate_unique_cafe_data(TEST_CAFES['cafe2'])
    cafe_in = CafeCreate(
        name=cafe_data['name'],
        address=cafe_data['address'],
        phone=cafe_data['phone'],
        description=cafe_data['description'],
        photo='',
        managers=[],
    )
    cafe_db = await get_cafe_crud().create(cafe_in, db_session)
    # Возвращаем объект модели из БД
    cafe = await db_session.get(Cafe, cafe_db.id)
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
async def test_table(db_session: AsyncSession, test_cafe: Cafe) -> None:
    """Фикстура для тестового стола (когда будет реализовано)."""
    table_in = TableCreate(
        seats_number=1,
        description='string',
    )
    table_crud = get_table_crud()
    table = await table_crud.create_table(
        cafe_id=test_cafe.id,
        obj_in=table_in,
        session=db_session,
    )
    return table


@pytest_asyncio.fixture
async def test_time_slot(
    db_session: AsyncSession,
    test_cafe: Cafe,
):
    """Создаёт тестовый временной слот с актуальной датой."""
    slot_crud = get_slot_crud()
    payload = SlotCreate(
        date=(date.today() + timedelta(days=3)).isoformat(),
        start_time='12:00:00',
        end_time='14:00:00',
        description='Fixture slot',
        is_active=True,
    )
    slot_obj = await slot_crud.create(
        payload,
        db_session,
        cafe_id=test_cafe.id,
    )
    return SimpleNamespace(
        id=slot_obj.id,
        start_time=slot_obj.start_time.strftime('%H:%M:%S'),
        end_time=slot_obj.end_time.strftime('%H:%M:%S'),
    )


@pytest_asyncio.fixture
async def test_action(
    db_session: AsyncSession,
    test_cafe: Cafe
) -> Action:
    """Фикстура для тестовой акции (когда будет реализовано)."""
    action_data = dict(TEST_ACTIONS['action1'])

    action_in = ActionCreate(
        cafe=test_cafe.id,
        description=action_data['description']
    )

    action = await actions_crud.create_action(
        obj_in=action_in,
        session=db_session,
    )

    return action


@pytest_asyncio.fixture
async def test_booking(
    db_session: AsyncSession,
    normal_user: User,
    test_cafe: Cafe,
    multiple_tables,
    multiple_slots,
) -> Any:
    """Создаёт тестовое бронирование для проверки эндпоинтов /booking/{id}."""
    booking_crud = get_booking_crud()
    booking_in = BookingCreate(
        user_id=normal_user.id,
        cafe_id=test_cafe.id,
        tables=[t.id for t in multiple_tables],
        slots=[s.id for s in multiple_slots],
        guests_number=4,
        note='Test booking fixture',
    )
    booking = await booking_crud.create_booking(
        obj_in=booking_in,
        session=db_session,
        user=normal_user,
    )

    assert booking.id is not None
    return booking


@pytest_asyncio.fixture
async def test_dish(
    db_session: AsyncSession,
    test_cafe: Cafe
) -> Any:
    """Фикстура для тестового блюда."""
    dish_data = {
        'cafe_id': test_cafe.id,
        'name': 'Test Dish',
        'description': 'Test dish description',
        'price': 100.00,
        'photo': 'test_photo.jpg',
        'is_active': True
    }
    dish = Dishe(**dish_data)
    db_session.add(dish)
    await db_session.commit()
    await db_session.refresh(dish)
    return dish


@pytest_asyncio.fixture
async def multiple_tables(db_session: AsyncSession, test_cafe: Cafe):
    """Создаёт два стола в кафе."""
    table_crud = get_table_crud()
    tables = []
    for i in range(2):
        table_in = TableCreate(seats_number=2 + i, description=f'Table {i}')
        table = await table_crud.create_table(
            cafe_id=test_cafe.id,
            obj_in=table_in,
            session=db_session,
        )
        tables.append(table)
    return tables


@pytest_asyncio.fixture
async def multiple_slots(db_session: AsyncSession, test_cafe: Cafe):
    """Создаёт два временных слота с разным временем."""
    slot_crud = get_slot_crud()
    base_date = date.today() + timedelta(days=3)
    slots = []
    times = [('12:00:00', '14:00:00'), ('15:00:00', '17:00:00')]

    for i, (start, end) in enumerate(times):
        payload = SlotCreate(
            date=base_date.isoformat(),
            start_time=start,
            end_time=end,
            description=f'Slot {i}',
            is_active=True,
        )
        slot = await slot_crud.create(
            payload,
            db_session,
            cafe_id=test_cafe.id
        )
        slots.append(slot)

    return slots


@pytest_asyncio.fixture
async def another_user_token(client_fixture: AsyncClient, another_user: User):
    """JWT-токен для второго пользователя."""
    payload = {
        'name': another_user.email,
        'password': VALID_PASSWORD,
    }
    response = await client_fixture.post('/auth/login', json=payload)
    assert response.status_code == 200, response.text
    return response.json()['token']
