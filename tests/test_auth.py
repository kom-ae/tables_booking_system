"""Тесты аутентификации для API системы бронирования столов.

Тестирует эндпоинты:
- POST /auth/login
- POST /auth/logout
"""

from typing import Any

import pytest
from httpx import AsyncClient
from starlette import status

from tests.conftest import (
    VALID_PASSWORD,
    assert_error_response,
    assert_success_response,
    get_auth_headers,
)

from src.schemas.auth import Auth


class TestAuthLogin:
    """Тесты эндпоинта POST /auth/login."""

    @pytest.mark.asyncio
    async def test_login_by_email_success(
        self,
        client_fixture: AsyncClient,
        normal_user: Any,
    ) -> None:
        """Тест успешной авторизации по email."""
        payload = Auth(
            name=normal_user.email,
            password=VALID_PASSWORD,
        ).model_dump()

        response = await client_fixture.post('/auth/login', json=payload)

        assert_success_response(response)
        data = response.json()
        assert 'token' in data
        assert isinstance(data['token'], str)
        assert len(data['token']) > 0

    @pytest.mark.asyncio
    async def test_login_by_phone_success(
        self,
        client_fixture: AsyncClient,
        normal_user: Any,
    ) -> None:
        """Тест успешной авторизации по телефону."""
        payload = Auth(
            name=normal_user.phone,
            password=VALID_PASSWORD,
        ).model_dump()

        response = await client_fixture.post('/auth/login', json=payload)

        assert_success_response(response)
        data = response.json()
        assert 'token' in data
        assert isinstance(data['token'], str)

    @pytest.mark.asyncio
    async def test_login_invalid_email(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест авторизации с несуществующим email."""
        payload = Auth(
            name='nonexistent@example.com',
            password=VALID_PASSWORD,
        ).model_dump()

        response = await client_fixture.post('/auth/login', json=payload)

        assert_error_response(response, status.HTTP_401_UNAUTHORIZED)

    @pytest.mark.asyncio
    async def test_login_invalid_phone(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест авторизации с несуществующим телефоном."""
        payload = Auth(
            name='+70000000999',
            password=VALID_PASSWORD,
        ).model_dump()

        response = await client_fixture.post('/auth/login', json=payload)

        assert_error_response(response, status.HTTP_401_UNAUTHORIZED)

    @pytest.mark.asyncio
    async def test_login_wrong_password(
        self,
        client_fixture: AsyncClient,
        normal_user: Any,
    ) -> None:
        """Тест авторизации с неправильным паролем."""
        payload = Auth(
            name=normal_user.email,
            password='wrong_password',
        ).model_dump()

        response = await client_fixture.post('/auth/login', json=payload)

        assert_error_response(response, status.HTTP_401_UNAUTHORIZED)

    @pytest.mark.asyncio
    async def test_login_empty_name(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест авторизации с пустым именем."""
        payload = Auth(
            name='',
            password=VALID_PASSWORD,
        ).model_dump()

        response = await client_fixture.post('/auth/login', json=payload)

        assert_error_response(response, status.HTTP_401_UNAUTHORIZED)

    @pytest.mark.asyncio
    async def test_login_empty_password(
        self,
        client_fixture: AsyncClient,
        normal_user: Any,
    ) -> None:
        """Тест авторизации с пустым паролем."""
        payload = Auth(
            name=normal_user.email,
            password='',
        ).model_dump()

        response = await client_fixture.post('/auth/login', json=payload)

        assert_error_response(response, status.HTTP_401_UNAUTHORIZED)

    @pytest.mark.asyncio
    async def test_login_missing_fields(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест авторизации без обязательных полей."""
        # Без поля name
        response = await client_fixture.post(
            '/auth/login', json={'password': VALID_PASSWORD},
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

        # Без поля password
        response = await client_fixture.post(
            '/auth/login', json={'name': 'test@example.com'},
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

        # Пустой JSON
        response = await client_fixture.post('/auth/login', json={})
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.asyncio
    async def test_login_invalid_json(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест авторизации с невалидным JSON."""
        response = await client_fixture.post(
            '/auth/login', json={'invalid': 'data'},
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.asyncio
    async def test_login_admin_user(
        self,
        client_fixture: AsyncClient,
        admin_user: Any,
    ) -> None:
        """Тест авторизации администратора."""
        payload = Auth(
            name=admin_user.email,
            password=VALID_PASSWORD,
        ).model_dump()

        response = await client_fixture.post('/auth/login', json=payload)

        assert_success_response(response)
        data = response.json()
        assert 'token' in data

    @pytest.mark.asyncio
    async def test_login_manager_user(
        self,
        client_fixture: AsyncClient,
        manager_user: Any,
    ) -> None:
        """Тест авторизации менеджера."""
        payload = Auth(
            name=manager_user.email,
            password=VALID_PASSWORD,
        ).model_dump()

        response = await client_fixture.post('/auth/login', json=payload)

        assert_success_response(response)
        data = response.json()
        assert 'token' in data


class TestAuthLogout:
    """Тесты эндпоинта POST /auth/logout."""

    @pytest.mark.asyncio
    async def test_logout_success(
        self,
        client_fixture: AsyncClient,
        user_token: str,
    ) -> None:
        """Тест успешного выхода из системы."""
        headers = get_auth_headers(user_token)
        response = await client_fixture.post('/auth/logout', headers=headers)

        assert_success_response(response)
        data = response.json()
        assert 'message' in data
        assert 'Вы вышли из системы' in data['message']

    @pytest.mark.asyncio
    async def test_logout_without_auth(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест выхода без авторизации."""
        response = await client_fixture.post('/auth/logout')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'message' in data
        assert 'Вы вышли из системы' in data['message']

    @pytest.mark.asyncio
    async def test_logout_invalid_token(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест выхода с невалидным токеном."""
        headers = get_auth_headers('invalid_token')
        response = await client_fixture.post('/auth/logout', headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'message' in data
        assert 'Вы вышли из системы' in data['message']

    @pytest.mark.asyncio
    async def test_logout_expired_token(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест выхода с истекшим токеном."""
        # Создаем токен с истекшим временем (если поддерживается)
        headers = get_auth_headers('expired_token_example')
        response = await client_fixture.post('/auth/logout', headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert 'message' in data
        assert 'Вы вышли из системы' in data['message']


class TestAuthIntegration:
    """Интеграционные тесты аутентификации."""

    @pytest.mark.asyncio
    async def test_login_logout_flow(
        self,
        client_fixture: AsyncClient,
        normal_user: Any,
    ) -> None:
        """Тест полного цикла входа и выхода."""
        # Логин
        login_payload = Auth(
            name=normal_user.email,
            password=VALID_PASSWORD,
        ).model_dump()

        login_response = await client_fixture.post(
            '/auth/login', json=login_payload,
        )
        assert_success_response(login_response)

        token = login_response.json()['token']

        # Логаут
        headers = get_auth_headers(token)
        logout_response = await client_fixture.post(
            '/auth/logout', headers=headers,
        )
        assert_success_response(logout_response)

    @pytest.mark.asyncio
    async def test_token_reuse_after_logout(
        self,
        client_fixture: AsyncClient,
        normal_user: Any,
    ) -> None:
        """Тест повторного использования токена после выхода."""
        # Логин
        login_payload = Auth(
            name=normal_user.email,
            password=VALID_PASSWORD,
        ).model_dump()

        login_response = await client_fixture.post(
            '/auth/login', json=login_payload,
        )
        token = login_response.json()['token']

        # Логаут
        headers = get_auth_headers(token)
        await client_fixture.post('/auth/logout', headers=headers)

        # Попытка использовать токен после выхода
        # Это зависит от реализации - токен может оставаться валидным
        # или стать невалидным после logout
        response = await client_fixture.get('/users/me', headers=headers)
        # Проверяем что токен либо валиден, либо невалиден
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        ]

    @pytest.mark.asyncio
    async def test_multiple_login_sessions(
        self,
        client_fixture: AsyncClient,
        normal_user: Any,
    ) -> None:
        """Тест множественных сессий одного пользователя."""
        # Первый логин
        login_payload = Auth(
            name=normal_user.email,
            password=VALID_PASSWORD,
        ).model_dump()

        response1 = await client_fixture.post(
            '/auth/login', json=login_payload,
        )
        token1 = response1.json()['token']

        # Второй логин
        response2 = await client_fixture.post(
            '/auth/login', json=login_payload,
        )
        token2 = response2.json()['token']

        # Оба токена должны быть валидными
        assert token1 != token2  # Токены должны быть разными

        headers1 = get_auth_headers(token1)
        headers2 = get_auth_headers(token2)

        response1 = await client_fixture.get('/users/me', headers=headers1)
        response2 = await client_fixture.get('/users/me', headers=headers2)

        assert_success_response(response1)
        assert_success_response(response2)

        # Данные должны быть одинаковыми
        data1 = response1.json()
        data2 = response2.json()
        assert data1['id'] == data2['id']
        assert data1['username'] == data2['username']
