# Запуск тестов:

Находясь в корневой дирректории проекта, в терминале выполнить команду:
```bash
# Активация виртуального окружения
source venv/bin/activate

# Установка переменных окружения для тестов
export JWT_ALGORITHM=HS256
export SECRET=test_secret
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=test
export DB_USER=test
export DB_PASSWORD=test

# Запуск всех тестов
python -m pytest tests/ -v

# Запуск только реализованных тестов (исключая пропущенные)
python -m pytest tests/ -v -m "not skip"

# Запуск конкретных тестов
python -m pytest tests/test_cafes.py -v
python -m pytest tests/test_auth.py -v
python -m pytest tests/test_users.py -v
```

# Руководство по тестированию API системы бронирования столов

## Обзор

Этот проект содержит комплексную систему тестов для API системы бронирования столов, написанную на основе API спецификации (`Спецификация API.yml`). За иселючением поля active, как и договаривались заменил в тестах на поле is_active.

## Структура тестов

```
tests/
├── conftest.py                 # Базовые фикстуры и конфигурация
├── test_auth.py               # Тесты аутентификации
├── test_users.py              # Тесты пользователей
├── test_cafes.py              # Тесты кафе
├── test_integration.py        # Интеграционные тесты
├── test_tables.py             # Тесты столов (будущие)
├── test_time_slots.py         # Тесты временных слотов (будущие)
├── test_actions.py            # Тесты акций (будущие)
├── test_dishes.py             # Тесты блюд (будущие)
├── test_bookings.py           # Тесты бронирований (будущие)
├── README.md                  # Это руководство
└── users/                     # Устаревшие тесты (можно удалить)
    ├── conftest.py
    ├── test_auth.py
    └── test_users.py
```

## Статус реализации

### ✅ Готовые к выполнению тесты

Эти тесты покрывают уже реализованную функциональность:

- **test_auth.py** - Тесты аутентификации (логин/логаут)
- **test_users.py** - Тесты управления пользователями
- **test_cafes.py** - Тесты управления кафе
- **test_integration.py** - Интеграционные тесты

### ⚠️ Будущие тесты

Эти тесты написаны на основе API спецификации, но пока не могут быть выполнены из-за отсутствующей реализации:

- **test_tables.py** - Тесты столов
- **test_time_slots.py** - Тесты временных слотов  
- **test_actions.py** - Тесты акций
- **test_dishes.py** - Тесты блюд (частично реализовано)
- **test_bookings.py** - Тесты бронирований

## Запуск тестов

### Все тесты
```bash
python -m pytest
```

### Только готовые тесты (исключая будущие)
```bash
python -m pytest -m "not skip"
```

### Конкретная группа тестов
```bash
python -m pytest tests/test_auth.py -v
python -m pytest tests/test_users.py -v
python -m pytest tests/test_cafes.py -v
python -m pytest tests/test_integration.py -v
```

### С подробным выводом
```bash
python -m pytest -v
```

### С покрытием кода
```bash
python -m pytest --cov=src
```

## Фикстуры

### Базовые фикстуры (conftest.py)

- `session_fixture` - Асинхронная сессия БД
- `client_fixture` - HTTP клиент для тестирования API
- `cleanup_db` - Автоматическая очистка БД перед каждым тестом

### Пользователи

- `admin_user` - Администратор
- `manager_user` - Менеджер  
- `normal_user` - Обычный пользователь
- `another_user` - Второй пользователь для тестов

### Токены авторизации

- `admin_token` - Токен администратора
- `manager_token` - Токен менеджера
- `user_token` - Токен обычного пользователя

### Кафе

- `test_cafe` - Тестовое кафе
- `test_cafe2` - Второе тестовое кафе

### Будущие фикстуры (когда будут реализованы)

- `test_table` - Тестовый стол
- `test_time_slot` - Тестовый временной слот
- `test_action` - Тестовая акция
- `test_dish` - Тестовое блюдо
- `test_booking` - Тестовое бронирование

## Константы для тестов

В `conftest.py` определены константы для тестирования:

```python
VALID_PASSWORD = 'Vx9!rT#4qLp$2mZ'
VALID_PHONE = '+70000000001'
VALID_EMAIL = 'test@example.com'
TEST_USERS = {...}  # Словарь с тестовыми пользователями
TEST_CAFES = {...}  # Словарь с тестовыми кафе
INVALID_DATA = {...}  # Невалидные данные для тестов валидации
```

## Эндпоинты API

В `conftest.py` определены все эндпоинты API в словаре `ENDPOINTS`:

```python
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
    'actions': {...},
    'bookings': {...},
    'dishes': {...},
    'tables': {...},
    'time_slots': {...},
}
```

## Утилиты для тестов

### Функции-помощники

- `get_auth_headers(token)` - Создание заголовков авторизации
- `assert_error_response(response, status, message)` - Проверка ошибочных ответов
- `assert_success_response(response, status)` - Проверка успешных ответов

### Утилиты для работы с эндпоинтами

- `get_endpoint_url(endpoint_type, action, **kwargs)` - Получение URL эндпоинта с подстановкой параметров
- `get_cafe_endpoint_url(action, cafe_id, **kwargs)` - Получение URL эндпоинта кафе
- `get_user_endpoint_url(action, user_id, **kwargs)` - Получение URL эндпоинта пользователя

## Типы тестов

### 1. Unit тесты
- Тесты отдельных эндпоинтов
- Тесты валидации данных
- Тесты обработки ошибок

### 2. Integration тесты
- Полные пользовательские сценарии
- Тесты взаимодействия компонентов
- Тесты безопасности и прав доступа

### 3. Security тесты
- Тесты авторизации
- Тесты прав доступа
- Тесты безопасности токенов

## Покрываемые сценарии

### Аутентификация (test_auth.py)
- ✅ Логин по email и телефону
- ✅ Валидация учетных данных
- ✅ Обработка ошибок авторизации
- ✅ Логаут
- ✅ Безопасность токенов

### Пользователи (test_users.py)
- ✅ CRUD операции для пользователей
- ✅ Права доступа (админ/пользователь)
- ✅ Валидация данных пользователей
- ✅ Управление профилем (/users/me)
- ✅ Фильтрация пользователей

### Кафе (test_cafes.py)
- ✅ CRUD операции для кафе
- ✅ Управление менеджерами кафе
- ✅ Валидация данных кафе
- ✅ Права доступа
- ✅ Фильтрация кафе (show_all параметр)
- ✅ Параметризованные тесты валидации
- ✅ Тесты с уникальными данными (timestamp)

### Интеграционные тесты (test_integration.py)
- ✅ Полный цикл регистрации и использования
- ✅ Административные функции
- ✅ Безопасность и права доступа
- ✅ Консистентность данных
- ✅ Обработка ошибок

## Особенности реализации тестов

### Параметризованные тесты

Многие тесты используют `@pytest.mark.parametrize` для уменьшения дублирования кода:

```python
@pytest.mark.parametrize("field,invalid_value,valid_fields", [
    ('name', 'x' * 300, {...}),
    ('address', 'x' * 300, {...}),
    ('phone', 'x' * 20, {...}),
])
async def test_cafe_field_validation(self, ...):
    # Тест выполняется для каждого набора параметров
```

### Уникальные данные в тестах

Для избежания конфликтов данных между тестами используются уникальные имена:

```python
import time
timestamp = int(time.time() * 1000)
payload = {
    'name': f'Test Cafe {timestamp}',
    'address': f'Test Address {timestamp}',
    'phone': f'+7000000{timestamp % 10000:04d}',
}
```

### Пропуск нереализованных тестов

Тесты для нереализованных модулей помечены как пропускаемые:

```python
pytestmark = pytest.mark.skip(reason="Actions endpoints not implemented yet")
```

### Правильная передача параметров

В тестах используется правильная передача параметров через `params`:

response = await client_fixture.get('/cafes/', params={'show_all': True})
