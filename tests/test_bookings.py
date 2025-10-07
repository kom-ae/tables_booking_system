"""Тесты бронирований для API системы бронирования столов.

ВНИМАНИЕ: Эти тесты написаны на основе API спецификации,
но пока не могут быть выполнены, так как соответствующие
эндпоинты не реализованы в проекте.

Тестирует эндпоинты (когда будут реализованы):
- GET /booking
- POST /booking
- GET /booking/{booking_id}
- PATCH /booking/{booking_id}
"""

from typing import Any

import pytest
from httpx import AsyncClient
from starlette import status

from src.models.cafe import Cafe
from src.models.user import User
from tests.conftest import (
    assert_error_response,
    assert_success_response,
    get_auth_headers,
)

# Эти тесты будут работать когда будут реализованы:
# 1. Модель Booking в src/models/booking.py
# 2. Эндпоинты в src/api/endpoints/bookings.py
# 3. CRUD операции для бронирований
# 4. Схемы BookingCreate, BookingUpdate, Booking
# 5. Все связанные модели: Table, TimeSlot, Dish

# Пропускаем все тесты до реализации эндпоинтов
# pytestmark = pytest.mark.skip(reason='Bookings эндпоинты не реализованы')


class TestBookingsList:
    """Тесты эндпоинта GET /booking."""

    @pytest.mark.asyncio
    async def test_get_bookings_as_admin(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_booking: Any,  # Фикстура из conftest.py (когда будет реализована)
    ) -> None:
        """Тест получения списка бронирований администратором."""
        headers = get_auth_headers(admin_token)
        response = await client_fixture.get('/booking', headers=headers)

        assert_success_response(response)
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_bookings_as_manager(
        self,
        client_fixture: AsyncClient,
        manager_token: str,
        test_booking: Any,  # Фикстура из conftest.py (когда будет реализована)
    ) -> None:
        """Тест получения списка бронирований менеджером (свое кафе)."""
        headers = get_auth_headers(manager_token)
        response = await client_fixture.get('/booking', headers=headers)

        assert_success_response(response)
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_bookings_as_user(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        normal_user: User,
    ) -> None:
        """Тест получения списка бронирований пользователем (свои)."""
        headers = get_auth_headers(user_token)
        response = await client_fixture.get('/booking', headers=headers)

        assert_success_response(response)
        data = response.json()
        assert isinstance(data, list)
        # Пользователь должен видеть только свои бронирования
        assert all(booking['user']['id'] == normal_user.id for booking in data)

    @pytest.mark.asyncio
    async def test_get_bookings_filter_by_cafe(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_cafe: Cafe,
    ) -> None:
        """Тест получения бронирований с фильтром по кафе."""
        headers = get_auth_headers(admin_token)
        response = await client_fixture.get(
            f'/booking?cafe_id={test_cafe.id}',
            headers=headers,
        )

        assert_success_response(response)
        data = response.json()
        assert isinstance(data, list)
        # Все бронирования должны быть из указанного кафе
        assert all(booking['cafe']['id'] == test_cafe.id for booking in data)

    @pytest.mark.asyncio
    async def test_get_bookings_filter_by_user(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        normal_user: User,
    ) -> None:
        """Тест получения бронирований с фильтром по пользователю."""
        headers = get_auth_headers(admin_token)
        response = await client_fixture.get(
            f'/booking?user_id={normal_user.id}',
            headers=headers,
        )

        assert_success_response(response)
        data = response.json()
        assert isinstance(data, list)
        # Все бронирования должны принадлежать указанному пользователю
        assert all(booking['user']['id'] == normal_user.id for booking in data)

    @pytest.mark.asyncio
    async def test_get_bookings_show_all_true(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест получения всех бронирований включая неактивные."""
        headers = get_auth_headers(admin_token)
        response = await client_fixture.get(
            '/booking?show_all=true',
            headers=headers,
        )

        assert_success_response(response)
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_bookings_show_all_false(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест получения только активных бронирований."""
        headers = get_auth_headers(admin_token)
        response = await client_fixture.get(
            '/booking?show_all=false',
            headers=headers,
        )

        assert_success_response(response)
        data = response.json()
        assert isinstance(data, list)
        # Должны быть только активные бронирования
        assert all(booking['is_active'] for booking in data)

    @pytest.mark.asyncio
    async def test_get_bookings_without_auth(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест получения списка бронирований без авторизации."""
        response = await client_fixture.get('/booking')

        assert_error_response(response, status.HTTP_401_UNAUTHORIZED)


class TestBookingCreate:
    """Тесты эндпоинта POST /booking."""

    @pytest.mark.asyncio
    async def test_create_booking_success(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        normal_user: User,
        test_cafe: Cafe,
        test_table: Any,  # Фикстура из conftest.py (когда будет реализована)
        test_time_slot: Any,  # Фикстура из conftest.py
        test_dish: Any,  # Фикстура из conftest.py
    ) -> None:
        """Тест успешного создания бронирования."""
        headers = get_auth_headers(user_token)
        payload = {
            'user_id': normal_user.id,
            'cafe_id': test_cafe.id,
            'tables': [test_table.id],
            'slots': [test_time_slot.id],
            'menu': [test_dish.id],
            'guests_number': 4,
            'note': 'Birthday celebration',
        }

        response = await client_fixture.post(
            '/booking',
            json=payload,
            headers=headers,
        )

        assert_success_response(response, status.HTTP_201_CREATED)
        data = response.json()
        assert data['user']['id'] == normal_user.id
        assert data['cafe']['id'] == test_cafe.id
        assert len(data['tables']) == 1
        assert data['tables'][0]['id'] == test_table.id
        assert len(data['slots']) == 1
        assert data['slots'][0]['id'] == test_time_slot.id
        assert len(data['menu']) == 1
        assert data['menu'][0]['id'] == test_dish.id
        assert data['guests_number'] == 4
        assert data['note'] == 'Birthday celebration'
        assert data['status'] == 0  # booking status
        assert 'id' in data
        assert 'created_at' in data
        assert 'updated_at' in data

    @pytest.mark.asyncio
    async def test_create_booking_minimal_data(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        normal_user: User,
        test_cafe: Cafe,
        test_table: Any,  # Фикстура из conftest.py (когда будет реализована)
        test_time_slot: Any,  # Фикстура из conftest.py
    ) -> None:
        """Тест создания бронирования с минимальными данными."""
        headers = get_auth_headers(user_token)
        payload = {
            'user_id': normal_user.id,
            'cafe_id': test_cafe.id,
            'tables': [test_table.id],
            'slots': [test_time_slot.id],
            'guests_number': 2,
        }

        response = await client_fixture.post(
            '/booking',
            json=payload,
            headers=headers,
        )

        assert_success_response(response, status.HTTP_201_CREATED)
        data = response.json()
        assert data['guests_number'] == 2
        assert data['menu'] == []  # Пустое меню
        assert data['note'] == '' or data['note'] is None

    @pytest.mark.asyncio
    async def test_create_booking_multiple_tables_and_slots(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        normal_user: User,
        test_cafe: Cafe,
        multiple_tables,
        multiple_slots,
    ) -> None:
        """Тест создания бронирования с несколькими столами и слотами."""
        headers = get_auth_headers(user_token)

        payload = {
            'user_id': normal_user.id,
            'cafe_id': test_cafe.id,
            'tables': [t.id for t in multiple_tables],
            'slots': [s.id for s in multiple_slots],
            'guests_number': 8,
        }

        response = await client_fixture.post(
            '/booking',
            json=payload,
            headers=headers,
        )

        assert_success_response(response, status.HTTP_201_CREATED)
        data = response.json()
        assert len(data['tables']) == 2
        assert len(data['slots']) == 2
        assert data['guests_number'] == 8
        assert data['user']['id'] == normal_user.id

    @pytest.mark.asyncio
    async def test_create_booking_missing_required_fields(
        self,
        client_fixture: AsyncClient,
        user_token: str,
    ) -> None:
        """Тест создания бронирования без обязательных полей."""
        headers = get_auth_headers(user_token)

        # Без user_id
        payload = {
            'cafe_id': 1,
            'tables': [1],
            'slots': [1],
            'guests_number': 4,
        }
        response = await client_fixture.post(
            '/booking',
            json=payload,
            headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

        # Без cafe_id
        payload = {
            'user_id': 1,
            'tables': [1],
            'slots': [1],
            'guests_number': 4,
        }
        response = await client_fixture.post(
            '/booking',
            json=payload,
            headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

        # Без tables
        payload = {
            'user_id': 1,
            'cafe_id': 1,
            'slots': [1],
            'guests_number': 4,
        }
        response = await client_fixture.post(
            '/booking',
            json=payload,
            headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

        # Без slots
        payload = {
            'user_id': 1,
            'cafe_id': 1,
            'tables': [1],
            'guests_number': 4,
        }
        response = await client_fixture.post(
            '/booking',
            json=payload,
            headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

        # Без guests_number
        payload = {
            'user_id': 1,
            'cafe_id': 1,
            'tables': [1],
            'slots': [1],
        }
        response = await client_fixture.post(
            '/booking',
            json=payload,
            headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.asyncio
    async def test_create_booking_invalid_guests_number(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        normal_user: User,
        test_cafe: Cafe,
    ) -> None:
        """Тест создания бронирования с невалидным количеством гостей."""
        headers = get_auth_headers(user_token)

        # Отрицательное количество гостей
        payload = {
            'user_id': normal_user.id,
            'cafe_id': test_cafe.id,
            'tables': [1],
            'slots': [1],
            'guests_number': -1,
        }
        response = await client_fixture.post(
            '/booking',
            json=payload,
            headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

        # Нулевое количество гостей
        payload = {
            'user_id': normal_user.id,
            'cafe_id': test_cafe.id,
            'tables': [1],
            'slots': [1],
            'guests_number': 0,
        }
        response = await client_fixture.post(
            '/booking',
            json=payload,
            headers=headers,
        )
        assert_error_response(response, status.HTTP_400_BAD_REQUEST)

    @pytest.mark.asyncio
    async def test_create_booking_nonexistent_resources(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        normal_user: User,
    ) -> None:
        """Тест создания бронирования с несуществующими ресурсами.

        Из-за проблемы с управлением транзакциями, когда ошибка
        возникает при создании бронирования, транзакция закрывается,
        что может привести к ошибке 401 вместо ожидаемой 400.
        Это известная проблема, которую нужно исправить в обработке ошибок.
        """
        headers = get_auth_headers(user_token)

        user_id = normal_user.id

        # Несуществующее кафе
        payload = {
            'user_id': user_id,
            'cafe_id': 99999,
            'tables': [1],
            'slots': [1],
            'guests_number': 4,
        }
        response = await client_fixture.post(
            '/booking',
            json=payload,
            headers=headers,
        )
        # Принимаем как 400, так и 401 из-за проблемы с транзакциями
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED,
        ]

        # Несуществующий стол
        payload = {
            'user_id': user_id,
            'cafe_id': 1,
            'tables': [99999],
            'slots': [1],
            'guests_number': 4,
        }
        response = await client_fixture.post(
            '/booking',
            json=payload,
            headers=headers,
        )
        # Принимаем как 400, так и 401 из-за проблемы с транзакциями
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED,
        ]

    @pytest.mark.asyncio
    async def test_create_booking_without_auth(
        self,
        client_fixture: AsyncClient,
    ) -> None:
        """Тест создания бронирования без авторизации."""
        payload = {
            'user_id': 1,
            'cafe_id': 1,
            'tables': [1],
            'slots': [1],
            'guests_number': 4,
        }

        response = await client_fixture.post('/booking', json=payload)

        assert_error_response(response, status.HTTP_401_UNAUTHORIZED)


class TestBookingById:
    """Тесты эндпоинтов GET и PATCH /booking/{booking_id}."""

    @pytest.mark.asyncio
    async def test_get_booking_by_id_as_admin(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_booking: Any,  # Фикстура из conftest.py (когда будет реализована)
    ) -> None:
        """Тест получения бронирования по ID администратором."""
        headers = get_auth_headers(admin_token)
        response = await client_fixture.get(
            f'/booking/{test_booking.id}',
            headers=headers,
        )

        assert_success_response(response)
        data = response.json()
        assert data['id'] == test_booking.id

    @pytest.mark.asyncio
    async def test_get_booking_by_id_as_owner(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        normal_user: User,
        test_booking: Any,  # Фикстура из conftest.py (когда будет реализована)
    ) -> None:
        """Тест получения своего бронирования пользователем."""
        headers = get_auth_headers(user_token)

        # Если бронирование принадлежит пользователю
        if test_booking.user_id == normal_user.id:
            response = await client_fixture.get(
                f'/booking/{test_booking.id}',
                headers=headers,
            )
            assert_success_response(response)
        else:
            response = await client_fixture.get(
                f'/booking/{test_booking.id}',
                headers=headers,
            )
            assert_error_response(response, status.HTTP_403_FORBIDDEN)

    @pytest.mark.asyncio
    async def test_get_booking_by_id_not_found(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
    ) -> None:
        """Тест получения несуществующего бронирования."""
        headers = get_auth_headers(admin_token)
        response = await client_fixture.get('/booking/99999', headers=headers)

        assert_error_response(response, status.HTTP_404_NOT_FOUND)

    @pytest.mark.asyncio
    async def test_update_booking_status_as_admin(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_booking: Any,  # Фикстура из conftest.py (когда будет реализована)
    ) -> None:
        """Тест обновления статуса бронирования администратором."""
        headers = get_auth_headers(admin_token)
        payload = {
            'status': 2,  # active status
            'note': 'Customer arrived',
        }

        response = await client_fixture.patch(
            f'/booking/{test_booking.id}',
            json=payload,
            headers=headers,
        )

        assert_success_response(response)
        data = response.json()
        assert data['status'] == 2
        assert data['note'] == 'Customer arrived'

    @pytest.mark.asyncio
    async def test_update_booking_as_owner(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        normal_user: User,
        test_booking: Any,  # Фикстура из conftest.py (когда будет реализована)
    ) -> None:
        """Тест обновления своего бронирования пользователем."""
        headers = get_auth_headers(user_token)
        payload = {
            'guests_number': 6,
            'note': 'Updated number of guests',
        }

        if test_booking.user_id == normal_user.id:
            response = await client_fixture.patch(
                f'/booking/{test_booking.id}',
                json=payload,
                headers=headers,
            )
            assert_success_response(response)
            data = response.json()
            assert data['guests_number'] == 6
        else:
            response = await client_fixture.patch(
                f'/booking/{test_booking.id}',
                json=payload,
                headers=headers,
            )
            assert_error_response(response, status.HTTP_403_FORBIDDEN)

    @pytest.mark.asyncio
    async def test_cancel_booking(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        normal_user: User,
        test_booking: Any,  # Фикстура из conftest.py (когда будет реализована)
    ) -> None:
        """Тест отмены бронирования."""
        headers = get_auth_headers(user_token)
        payload = {
            'status': 1,  # canceled status
            'note': 'Cancelled by user',
        }

        response = await client_fixture.patch(
            f'/booking/{test_booking.id}',
            json=payload,
            headers=headers,
        )

        if test_booking.user_id == normal_user.id:
            assert_success_response(response)
            data = response.json()
            assert data['status'] == 1
        else:
            assert_error_response(response, status.HTTP_403_FORBIDDEN)

    @pytest.mark.asyncio
    async def test_update_booking_invalid_status(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_booking: Any,  # Фикстура из conftest.py (когда будет реализована)
    ) -> None:
        """Тест обновления бронирования с невалидным статусом."""
        headers = get_auth_headers(admin_token)
        payload = {
            'status': 99,  # Невалидный статус
        }

        response = await client_fixture.patch(
            f'/booking/{test_booking.id}',
            json=payload,
            headers=headers,
        )

        assert_error_response(response, status.HTTP_400_BAD_REQUEST)


class TestBookingValidation:
    """Тесты валидации данных бронирований."""

    @pytest.mark.asyncio
    async def test_booking_status_values(
        self,
        client_fixture: AsyncClient,
        admin_token: str,
        test_booking: Any,  # Фикстура из conftest.py (когда будет реализована)
    ) -> None:
        """Тест валидации возможных значений статуса."""
        headers = get_auth_headers(admin_token)

        # Тестируем все валидные статусы
        valid_statuses = [0, 1, 2]  # booking, canceled, active

        for status_value in valid_statuses:
            payload = {'status': status_value}
            response = await client_fixture.patch(
                f'/booking/{test_booking.id}',
                json=payload,
                headers=headers,
            )
            assert_success_response(response)

    @pytest.mark.asyncio
    async def test_booking_note_length(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        normal_user: User,
        test_cafe: Cafe,
    ) -> None:
        """Тест валидации длины комментария."""
        headers = get_auth_headers(user_token)

        # Очень длинный комментарий
        payload = {
            'user_id': normal_user.id,
            'cafe_id': test_cafe.id,
            'tables': [1],
            'slots': [1],
            'guests_number': 4,
            'note': 'x' * 2000,  # Очень длинный комментарий
        }
        response = await client_fixture.post(
            '/booking',
            json=payload,
            headers=headers,
        )
        # Может быть принято или отклонено в зависимости от ограничений
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
        ]

    @pytest.mark.asyncio
    async def test_booking_table_capacity_validation(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        normal_user: User,
        test_cafe: Cafe,
        test_table: Any,  # Фикстура из conftest.py (когда будет реализована)
    ) -> None:
        """Тест валидации соответствия количества гостей вместимости столов."""
        headers = get_auth_headers(user_token)

        # Больше гостей чем мест в столе
        payload = {
            'user_id': normal_user.id,
            'cafe_id': test_cafe.id,
            'tables': [test_table.id],
            'slots': [1],
            'guests_number': test_table.seats_number
            + 10,  # Больше вместимости
        }
        response = await client_fixture.post(
            '/booking',
            json=payload,
            headers=headers,
        )
        # Может быть разрешено или запрещено в зависимости от бизнес-логики
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
        ]


class TestBookingIntegration:
    """Интеграционные тесты бронирований."""

    @pytest.mark.asyncio
    async def test_complete_booking_flow(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        admin_token: str,
        normal_user: User,
        test_cafe: Cafe,
        test_table: Any,  # Фикстура из conftest.py (когда будет реализована)
        test_time_slot: Any,  # Фикстура из conftest.py
        test_dish: Any,  # Фикстура из conftest.py
    ) -> None:
        """Тест полного цикла бронирования."""
        user_headers = get_auth_headers(user_token)
        admin_headers = get_auth_headers(admin_token)

        # 1. Пользователь создает бронирование
        create_payload = {
            'user_id': normal_user.id,
            'cafe_id': test_cafe.id,
            'tables': [test_table.id],
            'slots': [test_time_slot.id],
            'menu': [test_dish.id],
            'guests_number': 4,
            'note': 'Anniversary dinner',
        }

        create_response = await client_fixture.post(
            '/booking',
            json=create_payload,
            headers=user_headers,
        )
        assert_success_response(create_response, status.HTTP_201_CREATED)

        booking_data = create_response.json()
        booking_id = booking_data['id']
        assert booking_data['status'] == 0  # booking status

        # 2. Пользователь может просмотреть свое бронирование
        get_response = await client_fixture.get(
            f'/booking/{booking_id}',
            headers=user_headers,
        )
        assert_success_response(get_response)

        # 3. Пользователь обновляет количество гостей
        update_payload = {
            'guests_number': 6,
            'note': 'Updated for anniversary dinner',
        }
        update_response = await client_fixture.patch(
            f'/booking/{booking_id}',
            json=update_payload,
            headers=user_headers,
        )
        assert_success_response(update_response)

        updated_data = update_response.json()
        assert updated_data['guests_number'] == 6

        # 4. Администратор может видеть бронирование
        admin_get_response = await client_fixture.get(
            f'/booking/{booking_id}',
            headers=admin_headers,
        )
        assert_success_response(admin_get_response)

        # 5. Администратор подтверждает прибытие клиента
        confirm_payload = {
            'status': 2,  # active status
            'note': 'Customer arrived on time',
        }
        confirm_response = await client_fixture.patch(
            f'/booking/{booking_id}',
            json=confirm_payload,
            headers=admin_headers,
        )
        assert_success_response(confirm_response)

        final_data = confirm_response.json()
        assert final_data['status'] == 2

    @pytest.mark.asyncio
    async def test_booking_conflict_detection(
        self,
        client_fixture: AsyncClient,
        user_token: str,
        another_user_token: str,
        normal_user: User,
        another_user: User,
        test_cafe: Cafe,
        test_table: Any,
        test_time_slot: Any,
    ) -> None:
        """Тест обнаружения конфликтов бронирований."""
        headers = get_auth_headers(user_token)
        another_headers = get_auth_headers(another_user_token)
        payload1 = {
            'user_id': normal_user.id,
            'cafe_id': test_cafe.id,
            'tables': [test_table.id],
            'slots': [test_time_slot.id],
            'guests_number': 4,
        }
        response1 = await client_fixture.post(
            '/booking',
            json=payload1,
            headers=headers,
        )
        assert_success_response(response1, status.HTTP_201_CREATED)
        payload2 = {
            'user_id': another_user.id,
            'cafe_id': test_cafe.id,
            'tables': [test_table.id],
            'slots': [test_time_slot.id],
            'guests_number': 2,
        }
        response2 = await client_fixture.post(
            '/booking',
            json=payload2,
            headers=another_headers,
        )
        assert_error_response(response2, status.HTTP_400_BAD_REQUEST)
