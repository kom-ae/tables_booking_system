"""Базовые фикстуры и конфигурация для тестов API системы бронирования столов.

Этот модуль содержит общие фикстуры, константы и утилиты для всех тестов.
"""

import os
import uuid
from datetime import date, time
from types import SimpleNamespace
from typing import Any, AsyncGenerator, Dict

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette import status

from src.core.db import get_async_session
from src.crud.action import actions_crud
from src.crud.factory import get_cafe_crud, get_slot_crud, get_table_crud
from src.main import app
from src.models.base import BaseModel
from src.models.cafe import Cafe
from src.models.dish import Dishe
from src.models.table import Table
from src.models.user import User
from src.schemas.action import ActionCreate
from src.schemas.auth import Auth
from src.schemas.cafes import CafeCreate
from src.schemas.slots import SlotCreate
from src.schemas.table import TableCreate
from src.services.auth import PasswordService
from tests.database_manager import db_manager

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
# Базовые фикстуры
# -----------------------


# -----------------------
# Pytest hooks для параллельного выполнения
# -----------------------


def pytest_configure(config):
    """Настройка pytest перед запуском тестов."""
    # Получаем ID worker'а
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'master')
    if worker_id != 'master':
        print(f"[Worker {worker_id}] Configuring pytest...")


@pytest.fixture(scope='session', autouse=True)
def setup_test_database(request):
    """Настройка тестовой базы данных для worker'а (session scope)."""
    import asyncio

    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'master')
    print(f"[{worker_id}] Setting up test database...")

    # Создаем базу данных для worker'а
    async def _setup():
        await db_manager.create_database(worker_id)
        # Создаем таблицы
        engine = db_manager.get_engine(worker_id)
        async with engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.create_all)
        print(f"[{worker_id}] Database setup complete")

    asyncio.run(_setup())

    yield

    # Очистка после всех тестов
    async def _cleanup():
        print(f"[{worker_id}] Cleaning up test database...")
        await db_manager.dispose_all_engines()
        # Не удаляем БД чтобы можно было посмотреть состояние после тестов
        # await db_manager.drop_database(worker_id)

    asyncio.run(_cleanup())


# -----------------------
# Базовые фикстуры с транзакционной изоляцией
# -----------------------


@pytest_asyncio.fixture
async def db_engine():
    """Движок базы данных для текущего worker'а."""
    worker_id = os.environ.get('PYTEST_XDIST_WORKER', 'master')
    return db_manager.get_engine(worker_id)


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Транзакционная сессия для тестов.

    Каждый тест выполняется в своей транзакции, которая автоматически
    откатывается в конце теста для обеспечения изоляции.

    Поддерживает множественные commit через автоматическое создание новых savepoint.
    """
    # Создаем фабрику сессий
    session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Создаем сессию
    async with session_factory() as session:
        # Начинаем основную транзакцию
        async with session.begin():
            # Переопределяем commit для использования savepoints
            original_commit = session.commit

            async def savepoint_commit():
                """Commit через savepoint для поддержки множественных commit в тестах."""
                if session.in_transaction() and session.in_nested_transaction():
                    # Если мы в savepoint, просто flush
                    await session.flush()
                else:
                    # Если нет активного savepoint, создаем новый
                    await session.flush()

            session.commit = savepoint_commit

            # Создаем первый savepoint
            async with session.begin_nested():
                yield session

            # Восстанавливаем оригинальный commit
            session.commit = original_commit

            # Автоматически откатываем транзакцию в конце теста
            await session.rollback()


@pytest_asyncio.fixture
async def session_fixture(db_session: AsyncSession) -> AsyncSession:
    """
    Алиас для обратной совместимости со старыми тестами.

    Использует новую транзакционную сессию db_session.
    """
    return db_session


@pytest_asyncio.fixture
async def client_fixture(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient, None]:
    """
    AsyncClient для тестирования эндпоинтов FastAPI.

    Использует транзакционную сессию для изоляции тестов.
    """
    transport = ASGITransport(app=app)

    # Создаем генератор для dependency override
    async def get_test_session():
        yield db_session

    async with AsyncClient(
        transport=transport,
        base_url='http://testserver',
    ) as client:
        app.dependency_overrides[get_async_session] = get_test_session
        yield client
        app.dependency_overrides.clear()


# -----------------------
# Фикстуры пользователей
# -----------------------


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """
    Создаём администратора для тестов с уникальными данными.

    Генерирует уникальные email, username и phone для избежания
    конфликтов при параллельном выполнении тестов.
    """
    unique_suffix = str(uuid.uuid4())[:8]
    # Генерируем уникальный телефон с 10 цифрами после +7
    phone_suffix = str(uuid.uuid4().int)[:10].zfill(10)
    admin_data = TEST_USERS['admin']
    user = User(
        username=f"{admin_data['username']}_{unique_suffix}",
        email=f"{unique_suffix}_{admin_data['email']}",
        phone=f"+7{phone_suffix}",
        password=PasswordService.hash_password(admin_data['password']),
        role=admin_data['role'],
        tg_id=admin_data.get('tg_id'),
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def manager_user(db_session: AsyncSession) -> User:
    """
    Создаём менеджера для тестов с уникальными данными.

    Генерирует уникальные email, username и phone для избежания
    конфликтов при параллельном выполнении тестов.
    """
    unique_suffix = str(uuid.uuid4())[:8]
    # Генерируем уникальный телефон с 10 цифрами после +7
    phone_suffix = str(uuid.uuid4().int)[:10].zfill(10)
    manager_data = TEST_USERS['manager']
    user = User(
        username=f"{manager_data['username']}_{unique_suffix}",
        email=f"{unique_suffix}_{manager_data['email']}",
        phone=f"+7{phone_suffix}",
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
    """
    Создаём обычного пользователя для тестов с уникальными данными.

    Генерирует уникальные email, username и phone для избежания
    конфликтов при параллельном выполнении тестов.
    """
    unique_suffix = str(uuid.uuid4())[:8]
    # Генерируем уникальный телефон с 10 цифрами после +7
    phone_suffix = str(uuid.uuid4().int)[:10].zfill(10)
    user_data = TEST_USERS['user']
    user = User(
        username=f"{user_data['username']}_{unique_suffix}",
        email=f"{unique_suffix}_{user_data['email']}",
        phone=f"+7{phone_suffix}",
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
    """
    Создаём второго пользователя для тестов с уникальными данными.

    Генерирует уникальные email, username и phone для избежания
    конфликтов при параллельном выполнении тестов.
    """
    unique_suffix = str(uuid.uuid4())[:8]
    # Генерируем уникальный телефон с 10 цифрами после +7
    phone_suffix = str(uuid.uuid4().int)[:10].zfill(10)
    user_data = TEST_USERS['user2']
    user = User(
        username=f"{user_data['username']}_{unique_suffix}",
        email=f"{unique_suffix}_{user_data['email']}",
        phone=f"+7{phone_suffix}",
        password=PasswordService.hash_password(user_data['password']),
        role=user_data['role'],
        tg_id=user_data.get('tg_id'),
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user


# -----------------------
# Фикстуры кафе
# -----------------------


@pytest_asyncio.fixture
async def test_cafe(db_session: AsyncSession) -> Cafe:
    """
    Создаём тестовое кафе с уникальными данными.

    Генерирует уникальные name, address и phone для избежания
    конфликтов при параллельном выполнении тестов.
    """
    unique_suffix = str(uuid.uuid4())[:8]
    # Генерируем уникальный телефон с 10 цифрами после +7
    phone_suffix = str(uuid.uuid4().int)[:10].zfill(10)
    cafe_data = dict(TEST_CAFES['cafe1'])
    cafe_in = CafeCreate(
        name=f"{cafe_data['name']} {unique_suffix}",
        address=f"{cafe_data['address']} {unique_suffix}",
        phone=f"+7{phone_suffix}",
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
    """
    Создаём второе тестовое кафе с уникальными данными.

    Генерирует уникальные name, address и phone для избежания
    конфликтов при параллельном выполнении тестов.
    """
    unique_suffix = str(uuid.uuid4())[:8]
    # Генерируем уникальный телефон с 10 цифрами после +7
    phone_suffix = str(uuid.uuid4().int)[:10].zfill(10)
    cafe_data = dict(TEST_CAFES['cafe2'])
    cafe_in = CafeCreate(
        name=f"{cafe_data['name']} {unique_suffix}",
        address=f"{cafe_data['address']} {unique_suffix}",
        phone=f"+7{phone_suffix}",
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
    return {"Authorization": f"Bearer {token}"}


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
async def test_table(db_session: AsyncSession, test_cafe: Cafe) -> Table:
    """
    Фикстура для тестового стола.

    Использует транзакционную сессию для изоляции.
    """
    table_in = TableCreate(
        seats_number=1,
        description='Test table',
        is_active=True,
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
    """
    Создаём тестовый временной слот с уникальными данными.

    Использует транзакционную сессию для изоляции.
    """
    slot_crud = get_slot_crud()
    payload = SlotCreate(
        date=date(2025, 3, 10),
        start_time=time(12, 0, 0),
        end_time=time(14, 0, 0),
        description=f"Fixture slot {uuid.uuid4().hex[:8]}",
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
async def test_action(db_session: AsyncSession, test_cafe: Cafe) -> Any:
    """
    Фикстура для тестовой акции с уникальными данными.

    Использует транзакционную сессию для изоляции.
    """
    unique_suffix = str(uuid.uuid4())[:8]
    action_data = dict(TEST_ACTIONS['action1'])

    action_in = ActionCreate(
        cafe=test_cafe.id, description=f"{action_data['description']} {unique_suffix}"
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
) -> None:
    """Фикстура для тестового бронирования (когда будет реализовано)."""
    # TODO: Реализовать когда модель Booking будет готова
    pass


@pytest_asyncio.fixture
async def test_dish(db_session: AsyncSession, test_cafe: Cafe) -> Any:
    """
    Фикстура для тестового блюда с уникальными данными.

    Использует транзакционную сессию для изоляции.
    """
    unique_suffix = str(uuid.uuid4())[:8]
    dish_data = {
        'cafe_id': test_cafe.id,
        'name': f'Test Dish {unique_suffix}',
        'description': 'Test dish description',
        'price': 100.00,
        'photo': 'test_photo.jpg',
        'is_active': True,
    }
    dish = Dishe(**dish_data)
    db_session.add(dish)
    await db_session.flush()
    await db_session.refresh(dish)
    return dish
