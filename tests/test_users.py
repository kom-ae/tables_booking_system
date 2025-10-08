"""Тесты пользователей для API системы бронирования столов.

Тестирует эндпоинты:
- GET /users
- POST /users
- GET /users/{user_id}
- PATCH /users/{user_id}
- GET /users/me
- PATCH /users/me
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.models.user import User
from tests.conftest import (INVALID_DATA, VALID_PASSWORD,
                            assert_error_response, assert_success_response,
                            get_auth_headers)


class TestUsersList:
    """Тесты эндпоинта GET /users."""

    @pytest.mark.asyncio
    async def test_get_users_as_admin(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        admin_user: User,
        normal_user: User,
    ) -> None:
        """Тест получения списка пользователей администратором."""
        headers = get_auth_headers(admin_token)
        response = await client_fixture.get('/users', headers=headers)

        assert_success_response(response)
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # admin_user и normal_user

        # Проверяем что есть данные пользователей
        user_ids = [user['id'] for user in data]
        assert admin_user.id in user_ids
        assert normal_user.id in user_ids

    @pytest.mark.asyncio
    async def test_get_users_show_all_true(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        session_fixture: AsyncSession,
        admin_user: User,
        normal_user: User,
    ) -> None:
        """Тест получения всех пользователей включая неактивных."""
        # Деактивируем пользователя
        normal_user.is_active = False
        session_fixture.add(normal_user)
        await session_fixture.commit()

        headers = get_auth_headers(admin_token)
        response = await client_fixture.get(
            '/users?show_all=true',
            headers=headers,
        )

        assert_success_response(response)
        data = response.json()

        # Должны быть все пользователи включая неактивных
        user_ids = [user['id'] for user in data]
        assert admin_user.id in user_ids
        assert normal_user.id in user_ids

    @pytest.mark.asyncio
    async def test_get_users_show_all_false(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        session_fixture: AsyncSession,
        admin_user: User,
        normal_user: User,
    ) -> None:
        """Тест получения только активных пользователей."""
        # Деактивируем пользователя
        normal_user.is_active = False
        session_fixture.add(normal_user)
        await session_fixture.commit()

        headers = get_auth_headers(admin_token)
        response = await client_fixture.get(
            '/users?show_all=false',
            headers=headers,
        )

        assert_success_response(response)
        data = response.json()

        # Должны быть только активные пользователи
        assert all(user['is_active'] for user in data)
        user_ids = [user['id'] for user in data]
        assert admin_user.id in user_ids
        assert normal_user.id not in user_ids

    @pytest.mark.asyncio
    async def test_get_users_as_non_admin(
        self,
        client_fixture: AsyncClient,
        user_token: str,
    ) -> None:
        """Тест получения списка пользователей не-администратором."""
        headers = get_auth_headers(user_token)
        response = await client_fixture.get('/users', headers=headers)

        assert_error_response(response, status.HTTP_403_FORBIDDEN)

    @pytest.mark.asyncio
    async def test_get_users_without_auth(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест получения списка пользователей без авторизации."""
        response = await client_fixture.get('/users')

        assert_error_response(response, status.HTTP_401_UNAUTHORIZED)


class TestUserCreate:
    """Тесты эндпоинта POST /users."""

    @pytest.mark.asyncio
    async def test_create_user_success(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест успешного создания пользователя."""
        import uuid

        unique_suffix = str(uuid.uuid4())[:8]
        phone_suffix = str(uuid.uuid4().int)[:10].zfill(10)

        payload = {
            'username': f'newuser_{unique_suffix}',
            'email': f'{unique_suffix}_newuser@example.com',
            'phone': f'+7{phone_suffix}',
            'password': VALID_PASSWORD,
        }

        response = await client_fixture.post('/users', json=payload)

        assert_success_response(response, status.HTTP_201_CREATED)
        data = response.json()
        assert data['username'] == f'newuser_{unique_suffix}'
        assert data['email'] == f'{unique_suffix}_newuser@example.com'
        assert data['phone'] == f'+7{phone_suffix}'
        assert 'id' in data
        assert 'created_at' in data
        assert 'updated_at' in data

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(
        self,
        client_fixture: AsyncClient,
        normal_user: User,
    ) -> None:
        """Тест создания пользователя с дублирующимся email."""
        payload = {
            'username': 'different_user',
            'email': normal_user.email,  # Дублирующийся email
            'phone': '+70000000098',
            'password': VALID_PASSWORD,
        }

        response = await client_fixture.post('/users', json=payload)

        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.asyncio
    async def test_create_user_duplicate_phone(
        self,
        client_fixture: AsyncClient,
        normal_user: User,
    ) -> None:
        """Тест создания пользователя с дублирующимся телефоном."""
        payload = {
            'username': 'different_user',
            'email': 'different@example.com',
            'phone': normal_user.phone,  # Дублирующийся телефон
            'password': VALID_PASSWORD,
        }

        response = await client_fixture.post('/users', json=payload)

        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.asyncio
    async def test_create_user_invalid_email(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест создания пользователя с невалидным email."""
        payload = {
            'username': 'testuser',
            'email': INVALID_DATA['invalid_email'],
            'phone': '+70000000097',
            'password': VALID_PASSWORD,
        }

        response = await client_fixture.post('/users', json=payload)

        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.asyncio
    async def test_create_user_invalid_phone(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест создания пользователя с невалидным телефоном."""
        payload = {
            'username': 'testuser',
            'email': 'test@example.com',
            'phone': INVALID_DATA['invalid_phone'],
            'password': VALID_PASSWORD,
        }

        response = await client_fixture.post('/users', json=payload)

        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.asyncio
    async def test_create_user_weak_password(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест создания пользователя со слабым паролем."""
        payload = {
            'username': 'testuser',
            'email': 'test@example.com',
            'phone': '+70000000096',
            'password': INVALID_DATA['short_password'],
        }

        response = await client_fixture.post('/users', json=payload)

        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.asyncio
    async def test_create_user_missing_required_fields(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест создания пользователя без обязательных полей."""
        # Без username
        payload = {
            'email': 'test@example.com',
            'phone': '+70000000095',
            'password': VALID_PASSWORD,
        }
        response = await client_fixture.post('/users', json=payload)
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

        # Без phone
        payload = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': VALID_PASSWORD,
        }
        response = await client_fixture.post('/users', json=payload)
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

        # Без password
        payload = {
            'username': 'testuser',
            'email': 'test@example.com',
            'phone': '+70000000094',
        }
        response = await client_fixture.post('/users', json=payload)
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)


class TestUserById:
    """Тесты эндпоинтов GET /users/{user_id} и PATCH /users/{user_id}."""

    @pytest.mark.asyncio
    async def test_get_user_by_id_as_admin(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        normal_user: User,
    ) -> None:
        """Тест получения пользователя по ID администратором."""
        headers = get_auth_headers(admin_token)
        response = await client_fixture.get(
            f'/users/{normal_user.id}',
            headers=headers,
        )

        assert_success_response(response)
        data = response.json()
        assert data['id'] == normal_user.id
        assert data['username'] == normal_user.username
        assert data['email'] == normal_user.email

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест получения несуществующего пользователя."""
        headers = get_auth_headers(admin_token)
        response = await client_fixture.get('/users/99999', headers=headers)

        assert_error_response(response, status.HTTP_404_NOT_FOUND)

    @pytest.mark.asyncio
    async def test_get_user_by_id_as_non_admin(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        normal_user: User,
    ) -> None:
        """Тест получения пользователя по ID не-администратором."""
        headers = get_auth_headers(user_token)
        response = await client_fixture.get(
            f'/users/{normal_user.id}',
            headers=headers,
        )

        assert_error_response(response, status.HTTP_403_FORBIDDEN)

    @pytest.mark.asyncio
    async def test_update_user_by_id_as_admin(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        normal_user: User,
    ) -> None:
        """Тест обновления пользователя по ID администратором."""
        headers = get_auth_headers(admin_token)
        payload = {
            'username': 'updated_username',
            'email': 'updated@example.com',
        }

        response = await client_fixture.patch(
            f'/users/{normal_user.id}',
            json=payload,
            headers=headers,
        )

        assert_success_response(response)
        data = response.json()
        assert data['username'] == 'updated_username'
        assert data['email'] == 'updated@example.com'

    @pytest.mark.asyncio
    async def test_update_user_by_id_not_found(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест обновления несуществующего пользователя."""
        headers = get_auth_headers(admin_token)
        payload = {'username': 'updated_username'}

        response = await client_fixture.patch(
            '/users/99999',
            json=payload,
            headers=headers,
        )

        assert_error_response(response, status.HTTP_404_NOT_FOUND)

    @pytest.mark.asyncio
    async def test_update_user_by_id_as_non_admin(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        normal_user: User,
    ) -> None:
        """Тест обновления пользователя по ID не-администратором."""
        headers = get_auth_headers(user_token)
        payload = {'username': 'updated_username'}

        response = await client_fixture.patch(
            f'/users/{normal_user.id}',
            json=payload,
            headers=headers,
        )

        assert_error_response(response, status.HTTP_403_FORBIDDEN)


class TestCurrentUser:
    """Тесты эндпоинтов GET /users/me и PATCH /users/me."""

    @pytest.mark.asyncio
    async def test_get_current_user_success(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        normal_user: User,
    ) -> None:
        """Тест получения данных текущего пользователя."""
        headers = get_auth_headers(user_token)
        response = await client_fixture.get('/users/me', headers=headers)

        assert_success_response(response)
        data = response.json()
        assert data['id'] == normal_user.id
        assert data['username'] == normal_user.username
        assert data['email'] == normal_user.email

    @pytest.mark.asyncio
    async def test_get_current_user_without_auth(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест получения данных текущего пользователя без авторизации."""
        response = await client_fixture.get('/users/me')

        assert_error_response(response, status.HTTP_401_UNAUTHORIZED)

    @pytest.mark.asyncio
    async def test_update_current_user_success(
        self,
        client_fixture: AsyncClient,
        user_token: str,
    ) -> None:
        """Тест обновления данных текущего пользователя."""
        headers = get_auth_headers(user_token)
        payload = {
            'username': 'updated_username',
            'email': 'updated@example.com',
        }

        response = await client_fixture.patch(
            '/users/me',
            json=payload,
            headers=headers,
        )

        assert_success_response(response)
        data = response.json()
        assert data['username'] == 'updated_username'
        assert data['email'] == 'updated@example.com'

    @pytest.mark.asyncio
    async def test_update_current_user_password(
        self,
        client_fixture: AsyncClient,
        user_token: str,
    ) -> None:
        """Тест обновления пароля текущего пользователя."""
        headers = get_auth_headers(user_token)
        payload = {'password': 'NewPassword123!'}

        response = await client_fixture.patch(
            '/users/me',
            json=payload,
            headers=headers,
        )

        assert_success_response(response)
        # Пароль не должен возвращаться в ответе
        data = response.json()
        assert 'password' not in data

    @pytest.mark.asyncio
    async def test_update_current_user_invalid_data(
        self,
        client_fixture: AsyncClient,
        user_token: str,
    ) -> None:
        """Тест обновления текущего пользователя с невалидными данными."""
        headers = get_auth_headers(user_token)
        payload = {
            'email': INVALID_DATA['invalid_email'],
            'phone': INVALID_DATA['invalid_phone'],
        }

        response = await client_fixture.patch(
            '/users/me',
            json=payload,
            headers=headers,
        )

        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.asyncio
    async def test_update_current_user_without_auth(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест обновления текущего пользователя без авторизации."""
        payload = {'username': 'updated_username'}

        response = await client_fixture.patch('/users/me', json=payload)

        assert_error_response(response, status.HTTP_401_UNAUTHORIZED)


class TestUserValidation:
    """Тесты валидации данных пользователей."""

    @pytest.mark.asyncio
    async def test_username_validation(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест валидации имени пользователя."""
        # Слишком короткое имя
        payload = {
            'username': INVALID_DATA['empty_username'],
            'email': 'test@example.com',
            'phone': '+70000000093',
            'password': VALID_PASSWORD,
        }
        response = await client_fixture.post('/users', json=payload)
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

        # Слишком длинное имя
        payload = {
            'username': INVALID_DATA['long_username'],
            'email': 'test@example.com',
            'phone': '+70000000092',
            'password': VALID_PASSWORD,
        }
        response = await client_fixture.post('/users', json=payload)
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.asyncio
    async def test_password_validation(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест валидации пароля."""
        # Слабый пароль
        payload = {
            'username': 'testuser',
            'email': 'test@example.com',
            'phone': '+70000000091',
            'password': '123456',  # Слабый пароль
        }
        response = await client_fixture.post('/users', json=payload)
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.asyncio
    async def test_phone_format_validation(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест валидации формата телефона."""
        # Неправильный формат телефона
        payload = {
            'username': 'testuser',
            'email': 'test@example.com',
            'phone': INVALID_DATA['invalid_phone_format'],
            'password': VALID_PASSWORD,
        }
        response = await client_fixture.post('/users', json=payload)
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)
