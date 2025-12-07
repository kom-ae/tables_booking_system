# 🍽 Tables Booking System
> Веб-приложение для онлайн-бронирования столиков в ресторанах.
> Пользователи могут искать и бронировать столики, а администраторы — управлять заведениями и бронированиями.

## 🚀 Основной функционал

### 👤 Регистрация и авторизация пользователей
 - Вход по email или номеру телефона/паролю
 - Авторизация через JWT-токены

### 🍴 Бронирование столиков
- Поиск доступных столиков по дате и времени
- Создание, редактирование и отмена брони
- Проверка на пересечение времени бронирований
- Управление заведениями
- Добавление ресторанов и залов
- Настройка количества столиков
- Управление временем работы

### 🔔 Уведомления
Email уведомления о создании и изменении брони, напоминание о бронировании.

### 🛠️ Технологии
- Язык: Python 3.11
- Backend: FastAPI
- База данных: PostgreSQL + SQLAlchemy + Alembic
- Аутентификация: JWT
- Контейнеризация: Docker, Docker Compose
- Очереди и их мониторинг: Celery, Flower, RabbitMQ
- Тестирование: Pytest
- CI/CD: GitHub Actions
- Инфраструктура: Nginx, Gunicorn/Uvicorn

### 📂 Структура проекта
```bash
.
├── alembic/                     # Миграции БД
│   ├── env.py
│   └── versions/
│       └── migration.py
|   |
├── infra/                       # Инфраструктура и деплой
│   ├── docker-compose.local.yml - для локального запуска.
│   ├── docker-compose.production.yml - для запуска на сервере (образы DockerHub).
│   ├── docker-compose.test.yml - для запуска тестов.
│   └── pgdata/                  # Данные PostgreSQL
│
├── nginx/                       # Конфигурация Nginx
│   ├── local.conf
│   └── prod.conf
│
├── logs/                        # Логи проекта
|   └── app.log
|
├── src/                         # Исходный код приложения
│   ├── api/                     # Эндпоинты FastAPI
│   │   ├── endpoints/
│   │   ├── responses/
│   │   ├── routers.py
│   │   └── validators.py
│   │
│   ├── core/                    # Конфигурация, база данных, логирование
│   │   ├── base.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── logger.py
│   │   └── user.py
|   |
|   ├── celery/                  # Система очередей задач
│   │   ├── html/
|   |   ├── app.py
|   |   ├── formatters.py
|   |   ├── notifications.py
|   |   └── types.py
|   |
│   ├── crud/                    # CRUD-операции
|   |   ├── actions.py  - акции
|   |   ├── base.py - базовый
|   |   ├── bookings.py - бронирования
│   │   ├── cafes.py
│   │   ├── dishes.py
│   │   ├── tables.py
│   │   ├── users.py
|   |   ├── slots.py
│   │   └── factory.py
│   │
│   ├── exceptions/              # Кастомные исключения
|   |   ├── base.py
|   |   ├── bookings.py
|   |   ├── cafe.py
|   |   ├── handlers.py
|   |   ├── slots.py
│   │   ├── auth.py
│   │   ├── db.py
│   │   └── user.py
│   │
│   ├── models/                  # SQLAlchemy-модели
|   |   ├── action.py
|   |   ├── base.py
│   │   ├── booking.py
│   │   ├── cafe.py
│   │   ├── dish.py
|   |   ├── slot.py
│   │   ├── table.py
│   │   └── user.py
│   │
│   ├── schemas/                 # Pydantic-схемы
|   |   ├── action.py
│   │   ├── auth.py
|   |   ├── base.py
|   |   ├── bookings.py
│   │   ├── cafes.py
│   │   ├── dish.py
|   |   ├── slots.py
│   │   ├── table.py
│   │   ├── users.py
│   │   └── validators.py
│   │
│   ├── services/                # Бизнес-логика
│   │   ├── auth.py
│   │   └── slot_rules.py
│   │
|   ├── requirements.txt         # Основные зависимости
│   └── main.py                  # Точка входа в приложение
│
├── tests/                       # Тесты Pytest
│   ├── conftest.py
│   ├── database_manager.py
│   ├── test_actions.py
│   ├── test_bookings.py
│   ├── test_cafes.py
│   ├── test_config.py
│   ├── test_integration.py
│   ├── test_auth.py
│   ├── test_dishes.py
│   ├── test_tables.py
│   ├── test_time_slots.py
│   ├── test_transactional_example.py
│   ├── test_utils.py
│   └── test_users.py
│
├── AuthJWT.md                    # Инструкция по авторизации и схема работы
├── env.example                   # Образец для переменных окружения
├── env.test                      # Переменные окружения для тестирования
├── create_superuser_cli.py       # CLI-скрипт для создания суперпользователя
├── entrypoint.sh                 # Стартовый скрипт Docker
├── Dockerfile                    # Docker-образ для backend
├── requirements_dev.txt          # Основные зависимости для разработки
├── alembic.ini                   # Конфиг для Alembic
├── ruff.toml                     # Настройки линтера Ruff
├── pytest.ini                    # Конфиг для Pytest
└── README.md

```
### ⚙️ Установка и запуск

### Для локальной разработки

**Клонирование репозитория**
```bash
git clone https://github.com/Studio-Yandex-Practicum/tables_booking_system_team2.git
cd tables_booking_system_team2
```
### Настройка окружения
**Копируем файл окружения**
```bash
cd tables_booking_system_team2
cp env.example .env
```

### Запуск приложения локально
**С Docker (рекомендуется)**<br>
**Копируем .env в директорию infra**
```bash
cp .env infra/.env
```
### Запускаем контейнеры
```bash
cd src/infra
docker-compose -f docker-compose.local.yml up --build
```
**Без Docker**<br>
**Создание виртуального окружения**
```
python -m venv venv
source venv/bin/activate  # Linux/Mac
```
***или***
```bash
venv\Scripts\activate     # Windows
# Установка зависимостей
pip install -r requirements.txt
# Применение миграций
alembic upgrade head
```
### Запуск сервера
```bash
uvicorn src.main:app --reload

```
### Проверка работоспособности
**После запуска приложение будет доступно:**
- API: http://localhost
- Документация: http://localhost/docs
- Альтернативная документация: http://localhost/redoc<br>

**Приложение будет доступно по адресу:**<br>
👉 http://localhost/api/v1

**Документация API:**<br>
👉 Swagger UI: [http://localhost/docs](http://localhost/docs)<br>
👉 ReDoc: [http://localhost/redoc](http://localhost/redoc)

**🚀 Основные процессы CI/CD**<br>
### 🔄 CI/CD
Каждый коммит, push или pull request автоматически проверяется, тестируется и сопровождается уведомлением в Telegram.
| Workflow | Описание | Событие |
|-----------|-----------|---------|
| **develop.yml** | Запускает тесты посредством контейнера docker-compose.test.yml и проверяет корректность кода | push (branch - develop) |
| **main.yml** | Запускает тесты, отправляет уведомления в Telegram, выполняет деплой на сервер | push (branch - main) |
| **style_check.yml** | Проверяет стиль кода (Ruff, Pre-commit) | push, pull_request |
| **TelegramNotifications.yml** | Отправляет уведомления в Telegram об открытии Pull Request | pull request (branch - develop) |


**⚙️ Как это работает**<br>
- Разработчик делает push или pull request в репозиторий.
- GitHub Actions автоматически:
- собирает проект в Docker;
- прогоняет тесты;
- проверяет стиль кода;
- выполняет деплой на сервер (опционально)
- отправляет уведомление о результате в Telegram.
 -При успешной проверке или ошибке высылается сообщение в Telegram-чат разработчиков.

**📨 Пример уведомления в Telegram**
```bash
🍽 Сервис бронирования столиков<br>
🔔 Новое обновление в репозитории:<br>
Тип события: push<br>
Бранч: develop<br>
Коммит: 4dce9bd9edc6ad92ea1780c5428e3ad2df0ba109<br>
Автор: warqone<br>
Сообщение: Merge pull request #39 from Studio-Yandex-Practicum/features/crud_for_dishes<br>

Fix update crud dish
‼️ -- Подтяните к себе ветку develop -- ‼️
```
**📬 Если тесты или сборка не прошли — в Telegram отправляется<br>
     сообщение с ❌ и описанием ошибки.**<br>
Это позволяет команде оперативно реагировать и фиксить проблемы без необходимости проверять GitHub вручную.

### 🔑 Создание суперпользователя
Для создания суперпользователя, который будет иметь доступ ко всем
 административным функциям системы *в продакшене*, выполните следующие шаги:

**Запустите контейнеры с приложением:**<br>
Убедитесь, что ваше приложение запущено в Docker-контейнерах.
 Для этого выполните команду в директории,
  где находится ваш файл docker-compose.production.yml:
```bash
docker-compose -f docker-compose.production.yml up --build
```
**Запустите команду для создания суперпользователя:**<br>
После того как контейнеры будут запущены, используйте
 команду create_superuser для создания суперпользователя:<br>
***Примечание:***<br>
 Замените <имя_контейнера_backend> на реальное имя
 контейнера для вашего приложения, например, backend-1.
```bash
docker-compose exec <имя контейнера backend> sh python /app/create_superuser_cli.py create-superuser
```
**В процессе выполнения вас попросят ввести следующие данные:**<br>
- Username — имя пользователя (от 3 до 50 символов, только латиница, цифры и _)
- Email — email (например, user@example.com)
- Password — пароль (минимум 8 символов, строчные и заглавные буквы, цифры и спецсимволы)
- Phone — номер телефона (например, +79998887766)
- Telegram ID — (необязательно)

**Проверьте, что суперпользователь создан:**<br>
После успешного выполнения команды, вы увидите сообщение о том,
 что суперпользователь был создан.
  Теперь вы можете использовать его для доступа
   к административной панели вашего приложения.

### Тестирование

Проект настроен для параллельного выполнения тестов с транзакционной изоляцией на PostgreSQL в Docker контейнере.

#### Быстрый старт

**1. Запуск тестов**
```bash
# Запуск контейнера для тестов
docker-compose -f infra/docker-compose.test.yml up --build -d
```
После того как контейнер поднимется, тесты будут произведены автоматически.
в /logs появляется файл с логами тестов - test.log, либо можно просмотреть результаты тестов с помощью
```docker
docker compose -f infra/docker-compose.test.yml backend logs
```

#### Параллельное выполнение

Система поддерживает параллельное выполнение тестов с отдельными базами данных для каждого worker'а:
- **Master worker**: `test_db`
- **Worker gw0**: `test_db_gw0`
- **Worker gw1**: `test_db_gw1`
- И т.д.

Каждый тест выполняется в своей транзакции, которая автоматически откатывается.

#### Фильтрация тестов

```bash
# Только unit тесты
make test-fast

# Только интеграционные тесты
make test-integration

# Конкретные категории
make test-auth
make test-users
make test-cafes

# Конкретный файл
./run_tests.sh tests/test_auth.py

# Конкретный тест
./run_tests.sh tests/test_auth.py::TestAuth::test_login
```

#### Настройка окружения

Конфигурация в файле `env.test`:
```bash
# Основные настройки
DB_ENGINE=postgres
DB_HOST=localhost
DB_PORT=5433
DB_NAME=test_db
DB_USER=test_user
DB_PASSWORD=test_password

# JWT
SECRET=test_secret_key_for_testing_only
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### Написание тестов

```python
import pytest
from tests.test_utils import parallel_test, unit_test

class TestExample:
    @unit_test
    @parallel_test
    @pytest.mark.asyncio
    async def test_example(self, db_session: AsyncSession):
        # Тест с транзакционной изоляцией
        user = User(username='test', email='test@example.com', ...)
        db_session.add(user)
        await db_session.flush()  # НЕ commit!
        # Транзакция автоматически откатится в конце теста
```

#### Очистка тестовых данных

```bash
# Показать тестовые базы данных
./cleanup_test_databases.sh --dry-run

# Удалить все тестовые базы данных
./cleanup_test_databases.sh --all --force

# Очистка Docker volumes
make clean-docker
```

#### Отладка

```bash
# Последовательный режим для отладки
./run_tests.sh --serial --verbose

# Просмотр логов
tail -f test.log

# Подключение к тестовой БД
PGPASSWORD=test_password psql -h localhost -p 5433 -U test_user -d test_db
```

### 🌐 Деплой
- Backend запускается через Docker + Gunicorn/Uvicorn
- Nginx используется как реверс-прокси
- CI/CD настроен через GitHub Actions:
- запуск тестов
- сборка и публикация Docker-образа
- деплой на сервер

### 🧹 Стилизация и проверка кода
Для обеспечения единого стиля кода используются пакеты Ruff и Pre-commit.<br>

**Проверка стиля**
```sh
ruff check
```
**Проверка и автофикс**
```sh
ruff check --fix
```
**Автоматическая проверка при коммитах**<br>
Чтобы при каждом коммите автоматически проверялась и исправлялась стилистика, нужно подключить pre-commit:
```sh
pre-commit install
```

### 🧩 Примеры API-запросов
**👤 Регистрация пользователя**
```bash
POST /api/v1/auth/register
Content-Type: application/json


{
  "username": "IvanPetrov",
  "email": "user@example.com",
  "phone": "+75555555555",
  "tg_id": 123,
  "password": "IvanPetrov@1"
}

```
**✅ Ответ:**
```bash
{
  "username": "IvanPetrov",
  "email": "user@example.com",
  "phone": "+75555555555",
  "tg_id": 123,
  "id": 1,
  "is_active": true,
  "created_at": "2025-10-03T13:39:03.182Z",
  "updated_at": "2025-10-03T13:39:03.182Z"
}
```
**🔑 Авторизация (получение JWT)**
```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "sIvanPetrov@1"
}
```
**✅ Ответ:**
```bash
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI...",
}
```

### 👥 Команда разработки
**Проект создан в рамках обучения в Яндекс Практикуме.**<br>

**Наставник:**<br>
🧭 [Станислав Баринов](https://github.com/hixwizard")<br>

**Project Manager (PM):**<br>
📋 Александр Аваков<br>

**Тимлид:**<br>
🧑‍💻 [Вадим Каримов](https://github.com/warqone)<br>

**Разработчики:**<br>
💡 [Вадим Каримов](https://github.com/warqone) - Общая архитектура, ревью, Celery задачи (напоминания, уведомления), RabbitMQ, Flower<br>
💡 [Дмитрий Радюк](https://github.com/Dzmitry-Radziuk) - Auth (/auth) – логин/регистрация, JWT токены, Docker-compose, конфиги<br>
💡 [Александр Лавер](https://github.com/XanterXAlexandr) - Users (/users) – CRUD пользователей<br>
💡 [Александр Комаров](https://github.com/kom-ae) - Cafes (/cafes) – CRUD кафе, GitHub Actions, уведомления в группу ТГ при запросах на Pull Request и обновлениях в ветке develop<br>
💡 [Игорь Могилин](https://github.com/IgorMogilin) - Dishes (/dishes) – CRUD блюд, привязка к кафе<br>
💡 [Вика Долгова](https://github.com/VikaDroffa) - Bookings (/bookings) – бронирование столов/слотов, проверка пересечений, статусов, отмена, выбор блюд<br>
💡 [Алексей Гасилин](https://github.com/GasilinAlexei) - Slots (/cafe/slots) – CRUD слотов бронирования<br>
💡 [Дмитрий Волков](https://github.com/Divo190722) - Tables (/cafe/tables) – CRUD столов конкретного кафе<br>
💡 [Исхак Мурзаев](https://github.com/IskhakM) - Actions (/actions) – CRUD акций, привязка к кафе<br>
💡 [Михаил Яковенко](https://github.com/MikhailYakovenko) - Тесты, автотестирование, Docker-compose для тестирования<br>
