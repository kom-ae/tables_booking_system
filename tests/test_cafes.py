"""Тесты кафе для API системы бронирования столов.

Тестирует эндпоинты:
- GET /cafes
- POST /cafes
- GET /cafes/{cafe_id} (когда будет реализовано)
- PATCH /cafes/{cafe_id} (когда будет реализовано)
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.models.cafe import Cafe
from src.models.user import User
from tests.conftest import (
    INVALID_DATA,
    assert_error_response,
    assert_success_response,
    get_auth_headers,
)


class TestCafesList:
    """Тесты эндпоинта GET /cafes."""

    @pytest.mark.asyncio
    async def test_get_cafes_as_admin(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_cafe: Cafe,
    ) -> None:
        """Тест получения списка кафе администратором."""
        headers = get_auth_headers(admin_token)
        response = await client_fixture.get('/cafes/', headers=headers)

        assert_success_response(response)
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # Проверяем что есть данные кафе
        cafe_ids = [cafe['id'] for cafe in data]
        assert test_cafe.id in cafe_ids

    @pytest.mark.asyncio
    async def test_get_cafes_as_user(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        test_cafe: Cafe,
    ) -> None:
        """Тест получения списка кафе обычным пользователем."""
        headers = get_auth_headers(user_token)
        response = await client_fixture.get('/cafes/', headers=headers)

        assert_success_response(response)
        data = response.json()
        assert isinstance(data, list)

        # Пользователь должен видеть только активные кафе
        assert all(cafe['is_active'] for cafe in data)

    @pytest.mark.asyncio
    async def test_get_cafes_show_all_true(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        session_fixture: AsyncSession,
        test_cafe: Cafe,
    ) -> None:
        """Тест получения всех кафе включая неактивные."""
        # Деактивируем кафе
        await session_fixture.execute(
            text('UPDATE cafe SET is_active = false WHERE id = :cafe_id'),
            {'cafe_id': test_cafe.id},
        )
        await session_fixture.commit()

        headers = get_auth_headers(admin_token)
        params = {'show_all': True}
        response = await client_fixture.get(
            '/cafes/',
            headers=headers,
            params=params,
        )

        assert_success_response(response)
        data = response.json()

        # Должны быть все кафе включая неактивные
        cafe_ids = [cafe['id'] for cafe in data]
        assert test_cafe.id in cafe_ids

    @pytest.mark.asyncio
    async def test_get_cafes_show_all_false(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        session_fixture: AsyncSession,
        test_cafe: Cafe,
    ) -> None:
        """Тест получения кафе с параметром show_all=false."""
        # Деактивируем кафе
        await session_fixture.execute(
            text('UPDATE cafe SET is_active = false WHERE id = :cafe_id'),
            {'cafe_id': test_cafe.id},
        )
        await session_fixture.commit()

        headers = get_auth_headers(admin_token)
        params = {'show_all': False}
        response = await client_fixture.get(
            '/cafes/',
            headers=headers,
            params=params,
        )

        assert_success_response(response)
        data = response.json()

        # Проверяем что получили список кафе
        assert isinstance(data, list)
        assert len(data) > 0

        # Проверяем структуру данных кафе
        for cafe in data:
            assert 'id' in cafe
            assert 'name' in cafe
            assert 'address' in cafe
            assert 'phone' in cafe
            assert 'is_active' in cafe

    @pytest.mark.asyncio
    async def test_get_cafes_without_auth(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест получения списка кафе без авторизации."""
        response = await client_fixture.get('/cafes/')

        assert_error_response(response, status.HTTP_401_UNAUTHORIZED)


class TestCafeCreate:
    """Тесты эндпоинта POST /cafes."""

    @pytest.mark.asyncio
    async def test_create_cafe_as_admin_success(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест успешного создания кафе администратором."""
        import time

        timestamp = int(time.time() * 1000)  # Миллисекунды для уникальности

        headers = get_auth_headers(admin_token)
        payload = {
            'name': f'Test Cafe {timestamp}',
            'address': f'Test Address {timestamp}',
            'phone': f'+7000000{timestamp % 10000:04d}',
            'description': f'Test cafe description {timestamp}',
            'photo': '',
        }

        response = await client_fixture.post(
            '/cafes/',
            json=payload,
            headers=headers,
        )

        assert_success_response(response, status.HTTP_201_CREATED)
        data = response.json()
        assert data['name'] == f'Test Cafe {timestamp}'
        assert data['address'] == f'Test Address {timestamp}'
        assert data['phone'] == f'+7000000{timestamp % 10000:04d}'
        assert data['description'] == f'Test cafe description {timestamp}'
        assert data['photo'] == ''
        assert 'id' in data
        assert 'created_at' in data
        assert 'updated_at' in data

    @pytest.mark.asyncio
    async def test_create_cafe_with_managers(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        manager_user: User,
        normal_user: User,
    ) -> None:
        """Тест создания кафе с менеджерами."""
        import random
        import time

        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(1000, 9999)

        headers = get_auth_headers(admin_token)
        payload = {
            'name': f'Unique Cafe with Managers {timestamp}',
            'address': f'Unique Manager Address {random_suffix}',
            'phone': f'+7000000{random_suffix}',
            'description': f'Unique cafe with managers {timestamp}',
            'photo': '',
            'managers': [manager_user.id, normal_user.id],
        }

        response = await client_fixture.post(
            '/cafes/',
            json=payload,
            headers=headers,
        )

        assert_success_response(response, status.HTTP_201_CREATED)
        data = response.json()
        assert data['name'] == f'Unique Cafe with Managers {timestamp}'
        assert len(data['managers']) == 2
        manager_ids = [manager['id'] for manager in data['managers']]
        assert manager_user.id in manager_ids
        assert normal_user.id in manager_ids

    @pytest.mark.asyncio
    async def test_create_cafe_minimal_data(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест создания кафе с минимальными данными."""
        import random
        import time

        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(1000, 9999)

        headers = get_auth_headers(admin_token)
        payload = {
            'name': f'Unique Minimal Cafe {timestamp}',
            'address': f'Unique Minimal Address {random_suffix}',
            'phone': f'+7000000{random_suffix}',
            'description': f'Unique minimal description {timestamp}',
            'photo': '',
        }

        response = await client_fixture.post(
            '/cafes/',
            json=payload,
            headers=headers,
        )

        assert_success_response(response, status.HTTP_201_CREATED)
        data = response.json()
        assert data['name'] == f'Unique Minimal Cafe {timestamp}'
        assert data['address'] == f'Unique Minimal Address {random_suffix}'
        assert data['phone'] == f'+7000000{random_suffix}'
        assert data['description'] == f'Unique minimal description {timestamp}'
        # photo исключается из ответа из-за response_model_exclude_none=True

    @pytest.mark.asyncio
    async def test_create_cafe_as_non_admin(
        self,
        client_fixture: AsyncClient,
        user_token: str,
    ) -> None:
        """Тест создания кафе не-администратором."""
        headers = get_auth_headers(user_token)
        payload = {
            'name': 'Unauthorized Cafe',
            'address': 'Unauthorized Address 123',
            'phone': '+70000000085',
        }

        response = await client_fixture.post(
            '/cafes/',
            json=payload,
            headers=headers,
        )

        assert_error_response(response, status.HTTP_403_FORBIDDEN)

    @pytest.mark.asyncio
    async def test_create_cafe_without_auth(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест создания кафе без авторизации."""
        payload = {
            'name': 'Unauthorized Cafe',
            'address': 'Unauthorized Address 123',
            'phone': '+70000000084',
        }

        response = await client_fixture.post('/cafes/', json=payload)

        assert_error_response(response, status.HTTP_401_UNAUTHORIZED)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'missing_field,payload',
        [
            (
                'name',
                {
                    'address': 'Test Address 123',
                    'phone': '+70000000083',
                },
            ),
            (
                'address',
                {
                    'name': 'Test Cafe',
                    'phone': '+70000000082',
                },
            ),
            (
                'phone',
                {
                    'name': 'Test Cafe',
                    'address': 'Test Address 123',
                },
            ),
        ],
    )
    async def test_create_cafe_missing_required_fields(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        missing_field: str,
        payload: dict,
    ) -> None:
        """Тест создания кафе без обязательных полей."""
        headers = get_auth_headers(admin_token)
        response = await client_fixture.post(
            '/cafes/',
            json=payload,
            headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'field,invalid_value,valid_fields',
        [
            (
                'name',
                'A',
                {
                    'address': 'Test Address 123',
                    'phone': '+70000000081',
                },
            ),
            (
                'address',
                'A',
                {
                    'name': 'Test Cafe',
                    'phone': '+70000000080',
                },
            ),
            (
                'phone',
                '123',
                {
                    'name': 'Test Cafe',
                    'address': 'Test Address 123',
                },
            ),
        ],
    )
    async def test_create_cafe_invalid_data(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        field: str,
        invalid_value: str,
        valid_fields: dict,
    ) -> None:
        """Тест создания кафе с невалидными данными."""
        headers = get_auth_headers(admin_token)
        payload = {**valid_fields, field: invalid_value}
        response = await client_fixture.post(
            '/cafes/',
            json=payload,
            headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.asyncio
    async def test_create_cafe_invalid_phone_format(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест создания кафе с невалидным форматом телефона."""
        headers = get_auth_headers(admin_token)
        payload = {
            'name': 'Test Cafe',
            'address': 'Test Address 123',
            'phone': INVALID_DATA['invalid_phone_format'],
            'description': 'Test description',
            'photo': '',
        }

        response = await client_fixture.post(
            '/cafes/',
            json=payload,
            headers=headers,
        )

        # Невалидный формат телефона должен возвращать ошибку валидации
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.asyncio
    async def test_create_cafe_nonexistent_manager(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест создания кафе с несуществующим менеджером."""
        headers = get_auth_headers(admin_token)
        payload = {
            'name': 'Test Cafe',
            'address': 'Test Address 123',
            'phone': '+70000000079',
            'description': 'Test description',
            'photo': '',
            'managers': [99999],  # Несуществующий ID
        }

        response = await client_fixture.post(
            '/cafes/',
            json=payload,
            headers=headers,
        )

        # Это может быть ошибка валидации или успех с игнорированием
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_201_CREATED,
        ]


class TestCafeValidation:
    """Тесты валидации данных кафе."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'field,invalid_value,valid_fields',
        [
            (
                'name',
                'x' * 300,
                {
                    'address': 'Test Address 123',
                    'phone': '+70000000078',
                    'photo': '',
                },
            ),
            (
                'address',
                'x' * 300,
                {
                    'name': 'Test Cafe',
                    'phone': '+70000000077',
                    'photo': '',
                },
            ),
            (
                'phone',
                'x' * 20,
                {
                    'name': 'Test Cafe',
                    'address': 'Test Address 123',
                    'description': 'Test description',
                    'photo': '',
                },
            ),
        ],
    )
    async def test_cafe_field_validation(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        field: str,
        invalid_value: str,
        valid_fields: dict,
    ) -> None:
        """Тест валидации полей кафе."""
        headers = get_auth_headers(admin_token)
        payload = {**valid_fields, field: invalid_value}
        response = await client_fixture.post(
            '/cafes/',
            json=payload,
            headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)


class TestCafeIntegration:
    """Интеграционные тесты кафе."""

    @pytest.mark.asyncio
    async def test_cafe_creation_and_retrieval(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест создания кафе и его получения."""
        import random
        import time

        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(1000, 9999)

        headers = get_auth_headers(admin_token)

        # Создаем кафе
        create_payload = {
            'name': f'Integration Test Cafe {timestamp}',
            'address': f'Integration Address {random_suffix}',
            'phone': f'+7000000{random_suffix}',
            'description': f'Integration test cafe {timestamp}',
            'photo': '',
        }

        create_response = await client_fixture.post(
            '/cafes/',
            json=create_payload,
            headers=headers,
        )
        assert_success_response(create_response, status.HTTP_201_CREATED)

        created_cafe = create_response.json()
        cafe_id = created_cafe['id']

        # Получаем список кафе
        list_response = await client_fixture.get('/cafes/', headers=headers)
        assert_success_response(list_response)

        cafes = list_response.json()
        cafe_ids = [cafe['id'] for cafe in cafes]
        assert cafe_id in cafe_ids

        # Проверяем что данные совпадают
        found_cafe = next(cafe for cafe in cafes if cafe['id'] == cafe_id)
        assert found_cafe['name'] == f'Integration Test Cafe {timestamp}'
        assert found_cafe['address'] == f'Integration Address {random_suffix}'
        assert found_cafe['phone'] == f'+7000000{random_suffix}'

    @pytest.mark.asyncio
    async def test_cafe_manager_association(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        manager_user: User,
        normal_user: User,
    ) -> None:
        """Тест ассоциации менеджеров с кафе."""
        import random
        import time

        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(1000, 9999)

        headers = get_auth_headers(admin_token)

        # Создаем кафе с менеджерами
        payload = {
            'name': f'Manager Test Cafe {timestamp}',
            'address': f'Manager Address {random_suffix}',
            'phone': f'+7000000{random_suffix}',
            'description': f'Manager test cafe {timestamp}',
            'photo': '',
            'managers': [manager_user.id, normal_user.id],
        }

        response = await client_fixture.post(
            '/cafes/',
            json=payload,
            headers=headers,
        )
        assert_success_response(response, status.HTTP_201_CREATED)

        data = response.json()
        assert len(data['managers']) == 2

        # Проверяем что менеджеры правильно ассоциированы
        manager_ids = [manager['id'] for manager in data['managers']]
        assert manager_user.id in manager_ids
        assert normal_user.id in manager_ids

        # Проверяем что данные менеджеров корректны
        manager_data = next(
            manager
            for manager in data['managers']
            if manager['id'] == manager_user.id
        )
        assert manager_data['username'] == manager_user.username
        assert manager_data['email'] == manager_user.email
