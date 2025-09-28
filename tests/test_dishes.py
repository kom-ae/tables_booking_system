"""Тесты блюд для API системы бронирования столов.

ВНИМАНИЕ: Эти тесты написаны на основе API спецификации,
модель блюда частично реализована, но эндпоинты отсутствуют.

Тестирует эндпоинты (когда будут реализованы):
- GET /dishes
- POST /dishes
- GET /dishes/{dish_id}
- PATCH /dishes/{dish_id}
"""

from typing import Any

import pytest
from httpx import AsyncClient
from starlette import status

from tests.conftest import (
    assert_error_response,
    assert_success_response,
    get_auth_headers,
)

from src.models.cafes import Cafes

# Эти тесты будут работать когда будут реализованы:
# 1. Эндпоинты в src/api/endpoints/dishes.py
# 2. CRUD операции для блюд
# 3. Исправление модели Dish (добавление поля is_active)


class TestDishesList:
    """Тесты эндпоинта GET /dishes."""

    @pytest.mark.asyncio
    async def test_get_dishes_as_admin(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_dish: Any,  # Фикстура из conftest.py
    ) -> None:
        """Тест получения списка блюд администратором."""
        headers = get_auth_headers(admin_token)
        response = await client_fixture.get('/dishes', headers=headers)

        assert_success_response(response)
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_dishes_as_manager(
        self,
        client_fixture: AsyncClient,
        manager_token: str,
        test_dish: Any,  # Фикстура из conftest.py
    ) -> None:
        """Тест получения списка блюд менеджером."""
        headers = get_auth_headers(manager_token)
        response = await client_fixture.get('/dishes', headers=headers)

        assert_success_response(response)
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_dishes_as_user(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        test_dish: Any,  # Фикстура из conftest.py
    ) -> None:
        """Тест получения списка блюд обычным пользователем (активные)."""
        headers = get_auth_headers(user_token)
        response = await client_fixture.get('/dishes', headers=headers)

        assert_success_response(response)
        data = response.json()
        assert isinstance(data, list)
        # Пользователь должен видеть только активные блюда
        assert all(dish['is_active'] for dish in data)

    @pytest.mark.asyncio
    async def test_get_dishes_filter_by_cafe(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_cafe: Any,
    ) -> None:
        """Тест получения блюд с фильтром по кафе."""
        headers = get_auth_headers(admin_token)
        response = await client_fixture.get(
            f'/dishes?cafe_id={test_cafe.id}', headers=headers,
        )

        assert_success_response(response)
        data = response.json()
        assert isinstance(data, list)
        # Все блюда должны быть из указанного кафе
        assert all(dish['cafe']['id'] == test_cafe.id for dish in data)

    @pytest.mark.asyncio
    async def test_get_dishes_show_all_true(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест получения всех блюд включая неактивные."""
        headers = get_auth_headers(admin_token)
        response = await client_fixture.get(
            '/dishes?show_all=true', headers=headers,
        )

        assert_success_response(response)
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_dishes_show_all_false(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест получения только активных блюд."""
        headers = get_auth_headers(admin_token)
        url = "/dishes?show_all=false"
        response = await client_fixture.get(url, headers=headers)

        assert_success_response(response)
        data = response.json()
        assert isinstance(data, list)
        # Должны быть только активные блюда
        assert all(dish['is_active'] for dish in data)

    @pytest.mark.asyncio
    async def test_get_dishes_without_auth(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест получения списка блюд без авторизации."""
        response = await client_fixture.get('/dishes')

        assert_error_response(response, status.HTTP_401_UNAUTHORIZED)


class TestDishCreate:
    """Тесты эндпоинта POST /dishes."""

    @pytest.mark.asyncio
    async def test_create_dish_as_admin(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_cafe: Any,
    ) -> None:
        """Тест создания блюда администратором."""
        headers = get_auth_headers(admin_token)
        payload = {
            'cafe': test_cafe.id,
            'name': 'Delicious Pasta',
            'description': 'Italian pasta with tomato sauce',
            'price': 299.99,
            'photo': 'base64_encoded_photo_data',
        }

        response = await client_fixture.post(
            '/dishes', json=payload, headers=headers,
        )

        assert_success_response(response, status.HTTP_201_CREATED)
        data = response.json()
        assert data['cafe']['id'] == test_cafe.id
        assert data['name'] == 'Delicious Pasta'
        assert data['description'] == 'Italian pasta with tomato sauce'
        assert float(data['price']) == 299.99
        assert data['photo'] == 'base64_encoded_photo_data'
        assert 'id' in data
        assert 'created_at' in data
        assert 'updated_at' in data

    @pytest.mark.asyncio
    async def test_create_dish_as_manager(
        self,
        client_fixture: AsyncClient,
        manager_token: str,
        test_cafe: Any,
    ) -> None:
        """Тест создания блюда менеджером."""
        headers = get_auth_headers(manager_token)
        payload = {
            'cafe': test_cafe.id,
            'name': 'Manager Special',
            'description': 'Special dish by manager',
            'price': 199.99,
        }

        response = await client_fixture.post(
            '/dishes', json=payload, headers=headers,
        )

        assert_success_response(response, status.HTTP_201_CREATED)

    @pytest.mark.asyncio
    async def test_create_dish_as_user(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        test_cafe: Any,
    ) -> None:
        """Тест создания блюда обычным пользователем (запрещено)."""
        headers = get_auth_headers(user_token)
        payload = {
            'cafe': test_cafe.id,
            'name': 'Unauthorized Dish',
            'description': 'This should not be created',
            'price': 99.99,
        }

        response = await client_fixture.post(
            '/dishes', json=payload, headers=headers,
        )

        assert_error_response(response, status.HTTP_403_FORBIDDEN)

    @pytest.mark.asyncio
    async def test_create_dish_missing_required_fields(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест создания блюда без обязательных полей."""
        headers = get_auth_headers(admin_token)

        # Без cafe
        payload = {
            'name': 'Dish without cafe',
            'description': 'Description',
            'price': 100.00,
        }
        response = await client_fixture.post(
            '/dishes', json=payload, headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

        # Без name
        payload = {
            'cafe': 1,
            'description': 'Description',
            'price': 100.00,
        }
        response = await client_fixture.post(
            '/dishes', json=payload, headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

        # Без description
        payload = {
            'cafe': 1,
            'name': 'Dish name',
            'price': 100.00,
        }
        response = await client_fixture.post(
            '/dishes', json=payload, headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

        # Без price
        payload = {
            'cafe': 1,
            'name': 'Dish name',
            'description': 'Description',
        }
        response = await client_fixture.post(
            '/dishes', json=payload, headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.asyncio
    async def test_create_dish_invalid_price(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_cafe: Any,
    ) -> None:
        """Тест создания блюда с невалидной ценой."""
        headers = get_auth_headers(admin_token)

        # Отрицательная цена
        payload = {
            'cafe': test_cafe.id,
            'name': 'Invalid Dish',
            'description': 'Dish with negative price',
            'price': -10.00,
        }
        response = await client_fixture.post(
            '/dishes', json=payload, headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

        # Нулевая цена
        payload = {
            'cafe': test_cafe.id,
            'name': 'Free Dish',
            'description': 'Free dish',
            'price': 0.00,
        }
        response = await client_fixture.post(
            '/dishes', json=payload, headers=headers,
        )
        # Может быть разрешено или запрещено в зависимости от бизнес-логики
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
        ]

    @pytest.mark.asyncio
    async def test_create_dish_nonexistent_cafe(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест создания блюда для несуществующего кафе."""
        headers = get_auth_headers(admin_token)
        payload = {
            'cafe': 99999,  # Несуществующее кафе
            'name': 'Orphan Dish',
            'description': 'Dish without cafe',
            'price': 100.00,
        }

        response = await client_fixture.post(
            '/dishes', json=payload, headers=headers,
        )

        assert_error_response(response, status.HTTP_400_BAD_REQUEST)


class TestDishById:
    """Тесты эндпоинтов GET и PATCH /dishes/{dish_id}."""

    @pytest.mark.asyncio
    async def test_get_dish_by_id_as_admin(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_dish: Any,  # Фикстура из conftest.py
    ) -> None:
        """Тест получения блюда по ID администратором."""
        headers = get_auth_headers(admin_token)
        response = await client_fixture.get(
            f'/dishes/{test_dish.id}', headers=headers,
        )

        assert_success_response(response)
        data = response.json()
        assert data['id'] == test_dish.id
        assert data['name'] == test_dish.name
        assert data['description'] == test_dish.description

    @pytest.mark.asyncio
    async def test_get_dish_by_id_as_user_active(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        test_dish: Any,  # Фикстура из conftest.py
    ) -> None:
        """Тест получения активного блюда по ID пользователем."""
        headers = get_auth_headers(user_token)
        response = await client_fixture.get(
            f'/dishes/{test_dish.id}', headers=headers,
        )

        if test_dish.is_active:
            assert_success_response(response)
        else:
            assert_error_response(response, status.HTTP_404_NOT_FOUND)

    @pytest.mark.asyncio
    async def test_get_dish_by_id_not_found(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест получения несуществующего блюда."""
        headers = get_auth_headers(admin_token)
        response = await client_fixture.get('/dishes/99999', headers=headers)

        assert_error_response(response, status.HTTP_404_NOT_FOUND)

    @pytest.mark.asyncio
    async def test_update_dish_by_id_as_admin(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_dish: Any,  # Фикстура из conftest.py
        test_cafe2: Cafes,
    ) -> None:
        """Тест обновления блюда по ID администратором."""
        headers = get_auth_headers(admin_token)
        payload = {
            'cafe': test_cafe2.id,
            'name': 'Updated Dish Name',
            'description': 'Updated description',
            'price': 399.99,
            'photo': 'updated_base64_photo',
            'is_active': False,
        }

        response = await client_fixture.patch(
            f'/dishes/{test_dish.id}',
            json=payload,
            headers=headers,
        )

        assert_success_response(response)
        data = response.json()
        assert data['cafe']['id'] == test_cafe2.id
        assert data['name'] == 'Updated Dish Name'
        assert data['description'] == 'Updated description'
        assert float(data['price']) == 399.99
        assert data['photo'] == 'updated_base64_photo'
        assert data['is_active'] is False

    @pytest.mark.asyncio
    async def test_update_dish_as_user(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        test_dish: Any,  # Фикстура из conftest.py
    ) -> None:
        """Тест обновления блюда обычным пользователем (запрещено)."""
        headers = get_auth_headers(user_token)
        payload = {
            'name': 'Unauthorized Update',
            'description': 'This should not work',
        }

        response = await client_fixture.patch(
            f'/dishes/{test_dish.id}',
            json=payload,
            headers=headers,
        )

        assert_error_response(response, status.HTTP_403_FORBIDDEN)

    @pytest.mark.asyncio
    async def test_update_dish_invalid_price(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_dish: Any,  # Фикстура из conftest.py
    ) -> None:
        """Тест обновления блюда с невалидной ценой."""
        headers = get_auth_headers(admin_token)
        payload = {
            'price': -50.00,  # Отрицательная цена
        }

        response = await client_fixture.patch(
            f'/dishes/{test_dish.id}',
            json=payload,
            headers=headers,
        )

        assert_error_response(response, status.HTTP_400_BAD_REQUEST)


class TestDishValidation:
    """Тесты валидации данных блюд."""

    @pytest.mark.asyncio
    async def test_dish_name_length(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_cafe: Any,
    ) -> None:
        """Тест валидации длины названия блюда."""
        headers = get_auth_headers(admin_token)

        # Очень длинное название
        payload = {
            'cafe': test_cafe.id,
            'name': 'x' * 300,  # Очень длинное название
            'description': 'Description',
            'price': 100.00,
        }
        response = await client_fixture.post(
            '/dishes', json=payload, headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.asyncio
    async def test_dish_description_length(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_cafe: Any,
    ) -> None:
        """Тест валидации длины описания блюда."""
        headers = get_auth_headers(admin_token)

        # Очень длинное описание
        payload = {
            'cafe': test_cafe.id,
            'name': 'Valid Name',
            'description': 'x' * 1000,  # Очень длинное описание
            'price': 100.00,
        }
        response = await client_fixture.post(
            '/dishes', json=payload, headers=headers,
        )
        # Может быть принято или отклонено в зависимости от ограничений
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
        ]

    @pytest.mark.asyncio
    async def test_dish_price_precision(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_cafe: Any,
    ) -> None:
        """Тест валидации точности цены блюда."""
        headers = get_auth_headers(admin_token)

        # Цена с большой точностью
        payload = {
            'cafe': test_cafe.id,
            'name': 'Precise Price Dish',
            'description': 'Dish with precise price',
            'price': 123.456789,  # Много знаков после запятой
        }
        response = await client_fixture.post(
            '/dishes', json=payload, headers=headers,
        )

        if response.status_code == status.HTTP_201_CREATED:
            data = response.json()
            # Проверяем что цена округлена до правильной точности
            price = float(data['price'])
            # Ожидаем округление до 2 знаков после запятой
            assert abs(price - 123.46) < 0.01

    @pytest.mark.asyncio
    async def test_dish_special_characters(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_cafe: Any,
    ) -> None:
        """Тест создания блюда с специальными символами."""
        headers = get_auth_headers(admin_token)
        payload = {
            'cafe': test_cafe.id,
            'name': 'Café Latté ☕',
            'description': 'Delicious coffee with émojis 🌟 & chars áéíóú',
            'price': 45.50,
        }

        response = await client_fixture.post(
            '/dishes', json=payload, headers=headers,
        )

        assert_success_response(response, status.HTTP_201_CREATED)
        data = response.json()
        assert '☕' in data['name']
        assert '🌟' in data['description']
        assert 'áéíóú' in data['description']


class TestDishIntegration:
    """Интеграционные тесты блюд."""

    @pytest.mark.asyncio
    async def test_dish_creation_and_retrieval(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_cafe: Cafes,
    ) -> None:
        """Тест создания блюда и его получения."""
        headers = get_auth_headers(admin_token)

        # Создаем блюдо
        create_payload = {
            'cafe': test_cafe.id,
            'name': 'Integration Test Dish',
            'description': 'Dish for integration testing',
            'price': 250.00,
        }

        create_response = await client_fixture.post(
            '/dishes', json=create_payload, headers=headers,
        )
        assert_success_response(create_response, status.HTTP_201_CREATED)

        created_dish = create_response.json()
        dish_id = created_dish['id']

        # Получаем список блюд
        list_response = await client_fixture.get('/dishes', headers=headers)
        assert_success_response(list_response)

        dishes = list_response.json()
        dish_ids = [dish['id'] for dish in dishes]
        assert dish_id in dish_ids

        # Получаем блюдо по ID
        get_response = await client_fixture.get(
            f'/dishes/{dish_id}', headers=headers,
        )
        assert_success_response(get_response)

        dish_data = get_response.json()
        assert dish_data['id'] == dish_id
        assert dish_data['name'] == 'Integration Test Dish'
        assert float(dish_data['price']) == 250.00

    @pytest.mark.asyncio
    async def test_dish_cafe_association(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_cafe: Cafes,
        test_cafe2: Cafes,
    ) -> None:
        """Тест правильной ассоциации блюд с кафе."""
        headers = get_auth_headers(admin_token)

        # Создаем блюда для разных кафе
        dish1_payload = {
            'cafe': test_cafe.id,
            'name': 'Dish for Cafe 1',
            'description': 'First cafe dish',
            'price': 100.00,
        }

        dish2_payload = {
            'cafe': test_cafe2.id,
            'name': 'Dish for Cafe 2',
            'description': 'Second cafe dish',
            'price': 150.00,
        }

        response1 = await client_fixture.post(
            '/dishes', json=dish1_payload, headers=headers,
        )
        response2 = await client_fixture.post(
            '/dishes', json=dish2_payload, headers=headers,
        )

        assert_success_response(response1, status.HTTP_201_CREATED)
        assert_success_response(response2, status.HTTP_201_CREATED)

        # Проверяем фильтрацию по кафе
        cafe1_dishes_response = await client_fixture.get(
            f'/dishes?cafe_id={test_cafe.id}',
            headers=headers,
        )
        cafe2_dishes_response = await client_fixture.get(
            f'/dishes?cafe_id={test_cafe2.id}',
            headers=headers,
        )

        assert_success_response(cafe1_dishes_response)
        assert_success_response(cafe2_dishes_response)

        cafe1_dishes = cafe1_dishes_response.json()
        cafe2_dishes = cafe2_dishes_response.json()

        # Проверяем что блюда правильно фильтруются
        assert all(dish['cafe']['id'] == test_cafe.id for dish in cafe1_dishes)
        assert all(
            dish['cafe']['id'] == test_cafe2.id for dish in cafe2_dishes
        )
