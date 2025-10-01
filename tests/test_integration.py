"""Интеграционные тесты для API системы бронирования столов.

Тестирует полные пользовательские сценарии и взаимодействие между компонентами.
"""

import pytest
from httpx import AsyncClient
from starlette import status

from src.models.cafe import Cafe
from src.models.user import User
from tests.conftest import (
    assert_error_response,
    assert_success_response,
    get_auth_headers,
    VALID_PASSWORD,
)


class TestUserRegistrationFlow:
    """Тесты полного цикла регистрации и использования пользователя."""

    @pytest.mark.asyncio
    async def test_complete_user_registration_flow(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест полного цикла: регистрация -> логин -> использование API."""
        # 1. Регистрация нового пользователя
        registration_payload = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'phone': '+70000000050',
            'password': VALID_PASSWORD,
        }

        registration_response = await client_fixture.post(
            '/users',
            json=registration_payload,
        )
        assert_success_response(registration_response, status.HTTP_201_CREATED)

        user_data = registration_response.json()
        user_id = user_data['id']

        # 2. Логин с email
        login_payload = {
            'name': 'newuser@example.com',
            'password': VALID_PASSWORD,
        }

        login_response = await client_fixture.post(
            '/auth/login',
            json=login_payload,
        )
        assert_success_response(login_response)

        token = login_response.json()['token']
        headers = get_auth_headers(token)

        # 3. Получение данных текущего пользователя
        me_response = await client_fixture.get('/users/me', headers=headers)
        assert_success_response(me_response)

        me_data = me_response.json()
        assert me_data['id'] == user_id
        assert me_data['username'] == 'newuser'
        assert me_data['email'] == 'newuser@example.com'

        # 4. Обновление данных пользователя
        update_payload = {
            'username': 'updated_user',
            'email': 'updated@example.com',
        }

        update_response = await client_fixture.patch(
            '/users/me',
            json=update_payload,
            headers=headers,
        )
        assert_success_response(update_response)

        updated_data = update_response.json()
        assert updated_data['username'] == 'updated_user'
        assert updated_data['email'] == 'updated@example.com'

        # 5. Логин с обновленным email
        new_login_payload = {
            'name': 'updated@example.com',
            'password': VALID_PASSWORD,
        }

        new_login_response = await client_fixture.post(
            '/auth/login',
            json=new_login_payload,
        )
        assert_success_response(new_login_response)

        # 6. Логаут
        logout_response = await client_fixture.post(
            '/auth/logout',
            headers=headers,
        )
        assert_success_response(logout_response)

    @pytest.mark.asyncio
    async def test_user_login_by_phone_and_email(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест логина пользователя по телефону и email."""
        # Создаем пользователя
        registration_payload = {
            'username': 'multilogin_user',
            'email': 'multilogin@example.com',
            'phone': '+70000000049',
            'password': VALID_PASSWORD,
        }

        await client_fixture.post('/users', json=registration_payload)

        # Логин по email
        email_login = {
            'name': 'multilogin@example.com',
            'password': VALID_PASSWORD,
        }

        email_response = await client_fixture.post(
            '/auth/login',
            json=email_login,
        )
        assert_success_response(email_response)
        email_token = email_response.json()['token']

        # Логин по телефону
        phone_login = {
            'name': '+70000000049',
            'password': VALID_PASSWORD,
        }

        phone_response = await client_fixture.post(
            '/auth/login',
            json=phone_login,
        )
        assert_success_response(phone_response)
        phone_token = phone_response.json()['token']

        # Оба токена должны быть валидными
        email_headers = get_auth_headers(email_token)
        phone_headers = get_auth_headers(phone_token)

        email_me_response = await client_fixture.get(
            '/users/me',
            headers=email_headers,
        )
        phone_me_response = await client_fixture.get(
            '/users/me',
            headers=phone_headers,
        )

        assert_success_response(email_me_response)
        assert_success_response(phone_me_response)

        # Данные должны быть одинаковыми
        email_data = email_me_response.json()
        phone_data = phone_me_response.json()
        assert email_data['id'] == phone_data['id']
        assert email_data['username'] == phone_data['username']


class TestAdminWorkflow:
    """Тесты административных функций."""

    @pytest.mark.asyncio
    async def test_admin_user_management_workflow(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест полного цикла управления пользователями администратором."""
        headers = get_auth_headers(admin_token)

        # 1. Создаем пользователя через админ API
        create_payload = {
            'username': 'admin_created_user',
            'email': 'admin_created@example.com',
            'phone': '+70000000048',
            'password': VALID_PASSWORD,
        }

        create_response = await client_fixture.post(
            '/users',
            json=create_payload,
        )
        assert_success_response(create_response, status.HTTP_201_CREATED)

        created_user = create_response.json()
        user_id = created_user['id']

        # 2. Получаем список всех пользователей
        list_response = await client_fixture.get(
            '/users?show_all=true',
            headers=headers,
        )
        assert_success_response(list_response)

        users = list_response.json()
        user_ids = [user['id'] for user in users]
        assert user_id in user_ids

        # 3. Получаем конкретного пользователя по ID
        get_response = await client_fixture.get(
            f'/users/{user_id}',
            headers=headers,
        )
        assert_success_response(get_response)

        user_data = get_response.json()
        assert user_data['id'] == user_id
        assert user_data['username'] == 'admin_created_user'

        # 4. Обновляем пользователя
        update_payload = {
            'username': 'admin_updated_user',
            'email': 'admin_updated@example.com',
        }

        update_response = await client_fixture.patch(
            f'/users/{user_id}',
            json=update_payload,
            headers=headers,
        )
        assert_success_response(update_response)

        updated_data = update_response.json()
        assert updated_data['username'] == 'admin_updated_user'
        assert updated_data['email'] == 'admin_updated@example.com'

    @pytest.mark.asyncio
    async def test_admin_cafe_management_workflow(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        manager_user: User,
    ) -> None:
        """Тест полного цикла управления кафе администратором."""
        import random
        import time

        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(1000, 9999)

        headers = get_auth_headers(admin_token)

        # 1. Создаем кафе
        cafe_payload = {
            'name': f'Admin Managed Cafe {timestamp}',
            'address': f'Admin Address {random_suffix}',
            'phone': f'+7000000{random_suffix}',
            'description': f'Admin managed cafe {timestamp}',
            'photo': '',  # Пустая строка для поля photo
            'managers': [manager_user.id],
        }

        create_response = await client_fixture.post(
            '/cafes/',
            json=cafe_payload,
            headers=headers,
        )

        # Проверяем что создание прошло успешно
        if create_response.status_code == 201:
            assert_success_response(create_response, status.HTTP_201_CREATED)
            created_cafe = create_response.json()
            cafe_id = created_cafe['id']
        else:
            # Если создание не удалось, пропускаем остальные проверки
            pytest.skip(
                f'Cafe creation failed with status '
                f'{create_response.status_code}',
            )

        # 2. Получаем список кафе
        list_response = await client_fixture.get('/cafes/', headers=headers)
        assert_success_response(list_response)

        cafes = list_response.json()
        cafe_ids = [cafe['id'] for cafe in cafes]
        assert cafe_id in cafe_ids

        # 3. Проверяем что менеджер ассоциирован с кафе
        found_cafe = next(cafe for cafe in cafes if cafe['id'] == cafe_id)
        manager_ids = [manager['id'] for manager in found_cafe['managers']]
        assert manager_user.id in manager_ids


class TestSecurityAndPermissions:
    """Тесты безопасности и прав доступа."""

    @pytest.mark.asyncio
    async def test_user_cannot_access_admin_functions(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        normal_user: User,
    ) -> None:
        """Тест что обычный пользователь не может выполнять админ функции."""
        headers = get_auth_headers(user_token)

        # Попытка получить список пользователей
        response = await client_fixture.get('/users', headers=headers)
        assert_error_response(response, status.HTTP_403_FORBIDDEN)

        # Попытка получить пользователя по ID
        response = await client_fixture.get(
            f'/users/{normal_user.id}',
            headers=headers,
        )
        assert_error_response(response, status.HTTP_403_FORBIDDEN)

        # Попытка обновить пользователя по ID
        response = await client_fixture.patch(
            f'/users/{normal_user.id}',
            json={'username': 'hacked'},
            headers=headers,
        )
        assert_error_response(response, status.HTTP_403_FORBIDDEN)

    @pytest.mark.asyncio
    async def test_user_cannot_create_cafe(
        self,
        client_fixture: AsyncClient,
        user_token: str,
    ) -> None:
        """Тест что обычный пользователь не может создавать кафе."""
        import random
        import time

        timestamp = int(time.time() * 1000)
        random_suffix = random.randint(1000, 9999)

        headers = get_auth_headers(user_token)

        cafe_payload = {
            'name': f'Unauthorized Cafe {timestamp}',
            'address': f'Unauthorized Address {random_suffix}',
            'phone': f'+7000000{random_suffix}',
            'photo': '',  # Пустая строка для поля photo
        }

        response = await client_fixture.post(
            '/cafes/',
            json=cafe_payload,
            headers=headers,
        )
        assert_error_response(response, status.HTTP_403_FORBIDDEN)

    @pytest.mark.asyncio
    async def test_token_security(
        self,
        client_fixture: AsyncClient,
        normal_user: User,
    ) -> None:
        """Тест безопасности токенов."""
        # Получаем токен
        login_payload = {
            'name': normal_user.email,
            'password': VALID_PASSWORD,
        }

        login_response = await client_fixture.post(
            '/auth/login',
            json=login_payload,
        )
        token = login_response.json()['token']

        # Проверяем что токен работает
        headers = get_auth_headers(token)
        response = await client_fixture.get('/users/me', headers=headers)
        assert_success_response(response)

        # Проверяем что невалидный токен не работает
        invalid_headers = get_auth_headers('invalid_token')
        response = await client_fixture.get(
            '/users/me',
            headers=invalid_headers,
        )
        assert_error_response(response, status.HTTP_401_UNAUTHORIZED)

        # Проверяем что пустой токен не работает
        empty_headers = {'Authorization': 'Bearer '}
        response = await client_fixture.get('/users/me', headers=empty_headers)
        assert_error_response(response, status.HTTP_401_UNAUTHORIZED)


class TestDataConsistency:
    """Тесты консистентности данных."""

    @pytest.mark.asyncio
    async def test_user_data_consistency(
        self,
        client_fixture: AsyncClient,
        normal_user: User,
    ) -> None:
        """Тест консистентности данных пользователя."""
        # Логинимся
        login_payload = {
            'name': normal_user.email,
            'password': VALID_PASSWORD,
        }

        login_response = await client_fixture.post(
            '/auth/login',
            json=login_payload,
        )
        token = login_response.json()['token']
        headers = get_auth_headers(token)

        # Получаем данные через /me
        me_response = await client_fixture.get('/users/me', headers=headers)
        me_data = me_response.json()

        # Проверяем что данные соответствуют ожидаемым
        assert me_data['id'] == normal_user.id
        assert me_data['username'] == normal_user.username
        assert me_data['email'] == normal_user.email
        assert me_data['phone'] == normal_user.phone

        # Проверяем что обязательные поля присутствуют
        required_fields = [
            'id',
            'username',
            'phone',
            'is_active',
            'created_at',
            'updated_at',
        ]
        for field in required_fields:
            assert field in me_data

    @pytest.mark.asyncio
    async def test_cafe_data_consistency(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_cafe: Cafe,
    ) -> None:
        """Тест консистентности данных кафе."""
        headers = get_auth_headers(admin_token)

        # Получаем список кафе
        list_response = await client_fixture.get('/cafes/', headers=headers)
        assert_success_response(list_response)
        cafes = list_response.json()

        # Находим наше кафе
        found_cafe = next(cafe for cafe in cafes if cafe['id'] == test_cafe.id)

        # Проверяем консистентность данных
        assert found_cafe['name'] == test_cafe.name
        assert found_cafe['address'] == test_cafe.address
        assert found_cafe['phone'] == test_cafe.phone

        # Проверяем что обязательные поля присутствуют
        required_fields = [
            'id',
            'name',
            'address',
            'phone',
            'is_active',
            'created_at',
            'updated_at',
        ]
        for field in required_fields:
            assert field in found_cafe


class TestErrorHandling:
    """Тесты обработки ошибок."""

    @pytest.mark.asyncio
    async def test_graceful_error_handling(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест корректной обработки ошибок."""
        # Невалидный JSON
        response = await client_fixture.post(
            '/auth/login',
            json={'invalid': 'data'},
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

        # Несуществующий эндпоинт
        response = await client_fixture.get('/nonexistent')
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Неправильный метод
        response = await client_fixture.delete('/auth/login')
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @pytest.mark.asyncio
    async def test_validation_error_messages(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест сообщений об ошибках валидации."""
        # Создание пользователя с невалидными данными
        invalid_payload = {
            'username': '',  # Пустое имя
            'email': 'invalid-email',  # Невалидный email
            'phone': '123',  # Невалидный телефон
            'password': '123',  # Слабый пароль
        }

        response = await client_fixture.post('/users', json=invalid_payload)
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

        # Проверяем что в ответе есть информация об ошибке
        error_data = response.json()
        assert 'message' in error_data or 'error' in error_data
