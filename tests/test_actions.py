"""Тесты акций для API системы бронирования столов.

ВНИМАНИЕ: Эти тесты написаны на основе API спецификации,
но пока не могут быть выполнены, так как соответствующие
эндпоинты не реализованы в проекте.

Тестирует эндпоинты (когда будут реализованы):
- GET /actions
- POST /actions
- GET /actions/{action_id}
- PATCH /actions/{action_id}
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

# Эти тесты будут работать когда будут реализованы:
# 1. Модель Action в src/models/action.py
# 2. Эндпоинты в src/api/endpoints/actions.py
# 3. CRUD операции для акций
# 4. Схемы ActionCreate, ActionUpdate, Action


class TestActionsList:
    """Тесты эндпоинта GET /actions."""

    @pytest.mark.asyncio
    async def test_get_actions_as_admin(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_action: Any,  # Фикстура из conftest.py (когда будет реализована)
    ) -> None:
        """Тест получения списка акций администратором."""
        headers = get_auth_headers(admin_token)
        response = await client_fixture.get('/actions', headers=headers)

        assert_success_response(response)
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_actions_as_manager(
        self,
        client_fixture: AsyncClient,
        manager_token: str,
        test_action: Any,  # Фикстура из conftest.py (когда будет реализована)
    ) -> None:
        """Тест получения списка акций менеджером (только в своем кафе)."""
        headers = get_auth_headers(manager_token)
        response = await client_fixture.get('/actions', headers=headers)

        assert_success_response(response)
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_actions_as_user(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        test_action: Any,  # Фикстура из conftest.py (когда будет реализована)
    ) -> None:
        """Тест получения списка акций пользователем (только активные)."""
        headers = get_auth_headers(user_token)
        response = await client_fixture.get('/actions', headers=headers)

        assert_success_response(response)
        data = response.json()
        assert isinstance(data, list)
        # Пользователь должен видеть только активные акции
        assert all(action['is_active'] for action in data)

    @pytest.mark.asyncio
    async def test_get_actions_filter_by_cafe(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_cafe: Any,
    ) -> None:
        """Тест получения акций с фильтром по кафе."""
        headers = get_auth_headers(admin_token)
        response = await client_fixture.get(
            f'/actions?cafe_id={test_cafe.id}',
            headers=headers,
        )

        assert_success_response(response)
        data = response.json()
        assert isinstance(data, list)
        # Все акции должны быть из указанного кафе
        assert all(action['cafe']['id'] == test_cafe.id for action in data)

    @pytest.mark.asyncio
    async def test_get_actions_show_all_true(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест получения всех акций включая неактивные."""
        headers = get_auth_headers(admin_token)
        response = await client_fixture.get(
            '/actions?show_all=true',
            headers=headers,
        )

        assert_success_response(response)
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_actions_show_all_false(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест получения только активных акций."""
        headers = get_auth_headers(admin_token)
        response = await client_fixture.get(
            '/actions?show_all=false',
            headers=headers,
        )

        assert_success_response(response)
        data = response.json()
        assert isinstance(data, list)
        # Должны быть только активные акции
        assert all(action['is_active'] for action in data)

    @pytest.mark.asyncio
    async def test_get_actions_without_auth(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест получения списка акций без авторизации."""
        response = await client_fixture.get('/actions')

        assert_error_response(response, status.HTTP_401_UNAUTHORIZED)


class TestActionCreate:
    """Тесты эндпоинта POST /actions."""

    @pytest.mark.asyncio
    async def test_create_action_as_admin(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_cafe: Any,
    ) -> None:
        """Тест создания акции администратором."""
        headers = get_auth_headers(admin_token)
        payload = {
            'cafe': test_cafe.id,
            'description': 'Special discount 20% on all dishes',
        }

        response = await client_fixture.post(
            '/actions',
            json=payload,
            headers=headers,
        )

        assert_success_response(response, status.HTTP_201_CREATED)
        data = response.json()
        assert data['cafe']['id'] == test_cafe.id
        assert data['description'] == 'Special discount 20% on all dishes'
        assert 'id' in data
        assert 'created_at' in data
        assert 'updated_at' in data

    @pytest.mark.asyncio
    async def test_create_action_as_manager(
        self,
        client_fixture: AsyncClient,
        manager_token: str,
        test_cafe: Any,
    ) -> None:
        """Тест создания акции менеджером."""
        headers = get_auth_headers(manager_token)
        payload = {
            'cafe': test_cafe.id,
            'description': 'Manager special offer',
        }

        response = await client_fixture.post(
            '/actions',
            json=payload,
            headers=headers,
        )

        assert_success_response(response, status.HTTP_201_CREATED)

    @pytest.mark.asyncio
    async def test_create_action_as_user(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        test_cafe: Any,
    ) -> None:
        """Тест создания акции обычным пользователем (запрещено)."""
        headers = get_auth_headers(user_token)
        payload = {
            'cafe': test_cafe.id,
            'description': 'Unauthorized action',
        }

        response = await client_fixture.post(
            '/actions',
            json=payload,
            headers=headers,
        )

        assert_error_response(response, status.HTTP_403_FORBIDDEN)

    @pytest.mark.asyncio
    async def test_create_action_missing_required_fields(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест создания акции без обязательных полей."""
        headers = get_auth_headers(admin_token)

        # Без cafe
        payload = {
            'description': 'Action without cafe',
        }
        response = await client_fixture.post(
            '/actions',
            json=payload,
            headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

        # Без description
        payload = {
            'cafe': '1',
        }
        response = await client_fixture.post(
            '/actions',
            json=payload,
            headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.asyncio
    async def test_create_action_nonexistent_cafe(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест создания акции для несуществующего кафе."""
        headers = get_auth_headers(admin_token)
        payload = {
            'cafe': 99999,  # Несуществующее кафе
            'description': 'Action for nonexistent cafe',
        }

        response = await client_fixture.post(
            '/actions',
            json=payload,
            headers=headers,
        )

        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.asyncio
    async def test_create_action_empty_description(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_cafe: Any,
    ) -> None:
        """Тест создания акции с пустым описанием."""
        headers = get_auth_headers(admin_token)
        payload = {
            'cafe': test_cafe.id,
            'description': '',  # Пустое описание
        }

        response = await client_fixture.post(
            '/actions',
            json=payload,
            headers=headers,
        )

        assert_error_response(response, status.HTTP_400_BAD_REQUEST)


class TestActionById:
    """Тесты эндпоинтов GET и PATCH /actions/{action_id}."""

    @pytest.mark.asyncio
    async def test_get_action_by_id_as_admin(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_action: Any,  # Фикстура из conftest.py (когда будет реализована)
    ) -> None:
        """Тест получения акции по ID администратором."""
        headers = get_auth_headers(admin_token)
        response = await client_fixture.get(
            f'/actions/{test_action.id}',
            headers=headers,
        )

        assert_success_response(response)
        data = response.json()
        assert data['id'] == test_action.id
        assert data['description'] == test_action.description

    @pytest.mark.asyncio
    async def test_get_action_by_id_as_user_active(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        test_action: Any,  # Фикстура из conftest.py (когда будет реализована)
    ) -> None:
        """Тест получения активной акции по ID пользователем."""
        headers = get_auth_headers(user_token)
        response = await client_fixture.get(
            f'/actions/{test_action.id}',
            headers=headers,
        )

        if test_action.is_active:
            assert_success_response(response)
        else:
            assert_error_response(response, status.HTTP_404_NOT_FOUND)

    @pytest.mark.asyncio
    async def test_get_action_by_id_not_found(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест получения несуществующей акции."""
        headers = get_auth_headers(admin_token)
        response = await client_fixture.get('/actions/99999', headers=headers)

        assert_error_response(response, status.HTTP_404_NOT_FOUND)

    @pytest.mark.asyncio
    async def test_update_action_by_id_as_admin(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_action: Any,  # Фикстура из conftest.py (когда будет реализована)
        test_cafe2: Any,
    ) -> None:
        """Тест обновления акции по ID администратором."""
        headers = get_auth_headers(admin_token)
        payload = {
            'cafe': test_cafe2.id,
            'description': 'Updated action description',
            'is_active': False,
        }

        response = await client_fixture.patch(
            f'/actions/{test_action.id}',
            json=payload,
            headers=headers,
        )

        assert_success_response(response)
        data = response.json()
        assert data['cafe']['id'] == test_cafe2.id
        assert data['description'] == 'Updated action description'
        assert data['is_active'] is False

    @pytest.mark.asyncio
    async def test_update_action_as_user(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        test_action: Any,  # Фикстура из conftest.py (когда будет реализована)
    ) -> None:
        """Тест обновления акции обычным пользователем (запрещено)."""
        headers = get_auth_headers(user_token)
        payload = {
            'description': 'Unauthorized update',
        }

        response = await client_fixture.patch(
            f'/actions/{test_action.id}',
            json=payload,
            headers=headers,
        )

        assert_error_response(response, status.HTTP_403_FORBIDDEN)

    @pytest.mark.asyncio
    async def test_update_action_nonexistent_cafe(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_action: Any,  # Фикстура из conftest.py (когда будет реализована)
    ) -> None:
        """Тест обновления акции с несуществующим кафе."""
        headers = get_auth_headers(admin_token)
        payload = {
            'cafe': 99999,  # Несуществующее кафе
            'description': 'Updated description',
        }

        response = await client_fixture.patch(
            f'/actions/{test_action.id}',
            json=payload,
            headers=headers,
        )

        assert_error_response(response, status.HTTP_400_BAD_REQUEST)


class TestActionValidation:
    """Тесты валидации данных акций."""

    @pytest.mark.asyncio
    async def test_action_description_length(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_cafe: Any,
    ) -> None:
        """Тест валидации длины описания акции."""
        headers = get_auth_headers(admin_token)

        # Очень длинное описание
        payload = {
            'cafe': test_cafe.id,
            'description': 'x' * 2000,  # Очень длинное описание
        }
        response = await client_fixture.post(
            '/actions',
            json=payload,
            headers=headers,
        )
        # Может быть принято или отклонено в зависимости от ограничений
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
        ]

    @pytest.mark.asyncio
    async def test_action_special_characters(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_cafe: Any,
    ) -> None:
        """Тест создания акции с специальными символами в описании."""
        headers = get_auth_headers(admin_token)
        payload = {
            'cafe': test_cafe.id,
            'description': 'Special offer: 20% off! 🎉 Valid until 31/12/2024',
        }

        response = await client_fixture.post(
            '/actions',
            json=payload,
            headers=headers,
        )

        assert_success_response(response, status.HTTP_201_CREATED)
        data = response.json()
        assert '🎉' in data['description']


class TestActionIntegration:
    """Интеграционные тесты акций."""

    @pytest.mark.asyncio
    async def test_action_creation_and_retrieval(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_cafe: Any,
    ) -> None:
        """Тест создания акции и её получения."""
        headers = get_auth_headers(admin_token)

        # Создаем акцию
        create_payload = {
            'cafe': test_cafe.id,
            'description': 'Integration test action',
        }

        create_response = await client_fixture.post(
            '/actions',
            json=create_payload,
            headers=headers,
        )
        assert_success_response(create_response, status.HTTP_201_CREATED)

        created_action = create_response.json()
        action_id = created_action['id']

        # Получаем список акций
        list_response = await client_fixture.get('/actions', headers=headers)
        assert_success_response(list_response)

        actions = list_response.json()
        action_ids = [action['id'] for action in actions]
        assert action_id in action_ids

        # Получаем акцию по ID
        get_response = await client_fixture.get(
            f'/actions/{action_id}',
            headers=headers,
        )
        assert_success_response(get_response)

        action_data = get_response.json()
        assert action_data['id'] == action_id
        assert action_data['description'] == 'Integration test action'

    @pytest.mark.asyncio
    async def test_action_cafe_association(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_cafe: Any,
        test_cafe2: Any,
    ) -> None:
        """Тест правильной ассоциации акций с кафе."""
        headers = get_auth_headers(admin_token)

        # Создаем акции для разных кафе
        action1_payload = {
            'cafe': test_cafe.id,
            'description': 'Action for cafe 1',
        }

        action2_payload = {
            'cafe': test_cafe2.id,
            'description': 'Action for cafe 2',
        }

        response1 = await client_fixture.post(
            '/actions',
            json=action1_payload,
            headers=headers,
        )
        response2 = await client_fixture.post(
            '/actions',
            json=action2_payload,
            headers=headers,
        )

        assert_success_response(response1, status.HTTP_201_CREATED)
        assert_success_response(response2, status.HTTP_201_CREATED)

        # Проверяем фильтрацию по кафе
        cafe1_actions_response = await client_fixture.get(
            f'/actions?cafe_id={test_cafe.id}',
            headers=headers,
        )
        cafe2_actions_response = await client_fixture.get(
            f'/actions?cafe_id={test_cafe2.id}',
            headers=headers,
        )

        assert_success_response(cafe1_actions_response)
        assert_success_response(cafe2_actions_response)

        cafe1_actions = cafe1_actions_response.json()
        cafe2_actions = cafe2_actions_response.json()

        # Проверяем что акции правильно фильтруются
        assert all(
            action['cafe']['id'] == test_cafe.id for action in cafe1_actions
        )
        assert all(
            action['cafe']['id'] == test_cafe2.id for action in cafe2_actions
        )
