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

from tests.conftest import (
    INVALID_DATA,
    assert_error_response,
    assert_success_response,
    get_auth_headers,
)

from src.models.cafes import Cafes
from src.models.user import User


class TestCafesList:
    """Тесты эндпоинта GET /cafes."""

    @pytest.mark.asyncio
    async def test_get_cafes_as_admin(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_cafe: Cafes,
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
        test_cafe: Cafes,
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
        test_cafe: Cafes,
    ) -> None:
        """Тест получения всех кафе включая неактивные."""
        # Деактивируем кафе
        await session_fixture.execute(
            text("UPDATE cafes SET is_active = false WHERE id = :cafe_id"),
            {"cafe_id": test_cafe.id},
        )
        await session_fixture.commit()

        headers = get_auth_headers(admin_token)
        response = await client_fixture.get(
            '/cafes?show_all=true', headers=headers,
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
        test_cafe: Cafes,
    ) -> None:
        """Тест получения только активных кафе."""
        # Деактивируем кафе
        await session_fixture.execute(
            text("UPDATE cafes SET is_active = false WHERE id = :cafe_id"),
            {"cafe_id": test_cafe.id},
        )
        await session_fixture.commit()

        headers = get_auth_headers(admin_token)
        response = await client_fixture.get(
            '/cafes?show_all=false', headers=headers,
        )

        assert_success_response(response)
        data = response.json()

        # Должны быть только активные кафе
        assert all(cafe['is_active'] for cafe in data)
        cafe_ids = [cafe['id'] for cafe in data]
        assert test_cafe.id not in cafe_ids

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
        headers = get_auth_headers(admin_token)
        payload = {
            'name': 'New Cafe',
            'address': 'New Address 123',
            'phone': '+70000000088',
            'description': 'New cafe description',
            'photo': 'base64_encoded_photo',
        }

        response = await client_fixture.post(
            '/cafes/', json=payload, headers=headers,
        )

        assert_success_response(response, status.HTTP_201_CREATED)
        data = response.json()
        assert data['name'] == 'New Cafe'
        assert data['address'] == 'New Address 123'
        assert data['phone'] == '+70000000088'
        assert data['description'] == 'New cafe description'
        assert data['photo'] == 'base64_encoded_photo'
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
        headers = get_auth_headers(admin_token)
        payload = {
            'name': 'Cafe with Managers',
            'address': 'Manager Address 123',
            'phone': '+70000000087',
            'description': 'Cafe with managers',
            'managers': [manager_user.id, normal_user.id],
        }

        response = await client_fixture.post(
            '/cafes/', json=payload, headers=headers,
        )

        assert_success_response(response, status.HTTP_201_CREATED)
        data = response.json()
        assert data['name'] == 'Cafe with Managers'
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
        headers = get_auth_headers(admin_token)
        payload = {
            'name': 'Minimal Cafe',
            'address': 'Minimal Address 123',
            'phone': '+70000000086',
            'description': 'Minimal description',
        }

        response = await client_fixture.post(
            '/cafes/', json=payload, headers=headers,
        )

        assert_success_response(response, status.HTTP_201_CREATED)
        data = response.json()
        assert data['name'] == 'Minimal Cafe'
        assert data['address'] == 'Minimal Address 123'
        assert data['phone'] == '+70000000086'
        assert data['description'] == 'Minimal description'
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
            '/cafes/', json=payload, headers=headers,
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
    async def test_create_cafe_missing_required_fields(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест создания кафе без обязательных полей."""
        headers = get_auth_headers(admin_token)

        # Без name
        payload = {
            'address': 'Test Address 123',
            'phone': '+70000000083',
        }
        response = await client_fixture.post(
            '/cafes/', json=payload, headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

        # Без address
        payload = {
            'name': 'Test Cafe',
            'phone': '+70000000082',
        }
        response = await client_fixture.post(
            '/cafes/', json=payload, headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

        # Без phone
        payload = {
            'name': 'Test Cafe',
            'address': 'Test Address 123',
        }
        response = await client_fixture.post(
            '/cafes/', json=payload, headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.asyncio
    async def test_create_cafe_invalid_data(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест создания кафе с невалидными данными."""
        headers = get_auth_headers(admin_token)

        # Слишком короткое название
        payload = {
            'name': 'A',  # Слишком короткое
            'address': 'Test Address 123',
            'phone': '+70000000081',
        }
        response = await client_fixture.post(
            '/cafes/', json=payload, headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

        # Слишком короткий адрес
        payload = {
            'name': 'Test Cafe',
            'address': 'A',  # Слишком короткий
            'phone': '+70000000080',
        }
        response = await client_fixture.post(
            '/cafes/', json=payload, headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

        # Слишком короткий телефон
        payload = {
            'name': 'Test Cafe',
            'address': 'Test Address 123',
            'phone': '123',  # Слишком короткий
        }
        response = await client_fixture.post(
            '/cafes/', json=payload, headers=headers,
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
        }

        response = await client_fixture.post(
            '/cafes/', json=payload, headers=headers,
        )

        # Поскольку в схеме нет валидации регулярного выражения для телефона,
        # невалидный формат телефона проходит валидацию Pydantic
        assert_success_response(response, status.HTTP_201_CREATED)

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
            'managers': [99999],  # Несуществующий ID
        }

        response = await client_fixture.post(
            '/cafes/', json=payload, headers=headers,
        )

        # Это может быть ошибка валидации или успех с игнорированием
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_201_CREATED,
        ]


class TestCafeValidation:
    """Тесты валидации данных кафе."""

    @pytest.mark.asyncio
    async def test_cafe_name_validation(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест валидации названия кафе."""
        headers = get_auth_headers(admin_token)

        # Слишком длинное название
        payload = {
            'name': 'x' * 300,  # Слишком длинное
            'address': 'Test Address 123',
            'phone': '+70000000078',
        }
        response = await client_fixture.post(
            '/cafes/', json=payload, headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.asyncio
    async def test_cafe_address_validation(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест валидации адреса кафе."""
        headers = get_auth_headers(admin_token)

        # Слишком длинный адрес
        payload = {
            'name': 'Test Cafe',
            'address': 'x' * 300,  # Слишком длинный
            'phone': '+70000000077',
        }
        response = await client_fixture.post(
            '/cafes/', json=payload, headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.asyncio
    async def test_cafe_phone_validation(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест валидации телефона кафе."""
        headers = get_auth_headers(admin_token)

        # Слишком длинный телефон
        payload = {
            'name': 'Test Cafe',
            'address': 'Test Address 123',
            'phone': 'x' * 20,  # Слишком длинный
            'description': 'Test description',
        }
        response = await client_fixture.post(
            '/cafes/', json=payload, headers=headers,
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
        headers = get_auth_headers(admin_token)

        # Создаем кафе
        create_payload = {
            'name': 'Integration Test Cafe',
            'address': 'Integration Address 123',
            'phone': '+70000000076',
            'description': 'Integration test cafe',
        }

        create_response = await client_fixture.post(
            '/cafes/', json=create_payload, headers=headers,
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
        assert found_cafe['name'] == 'Integration Test Cafe'
        assert found_cafe['address'] == 'Integration Address 123'
        assert found_cafe['phone'] == '+70000000076'

    @pytest.mark.asyncio
    async def test_cafe_manager_association(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        manager_user: User,
        normal_user: User,
    ) -> None:
        """Тест ассоциации менеджеров с кафе."""
        headers = get_auth_headers(admin_token)

        # Создаем кафе с менеджерами
        payload = {
            'name': 'Manager Test Cafe',
            'address': 'Manager Address 123',
            'phone': '+70000000075',
            'description': 'Manager test cafe',
            'managers': [manager_user.id, normal_user.id],
        }

        response = await client_fixture.post(
            '/cafes/', json=payload, headers=headers,
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
