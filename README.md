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
Email/Telegram-уведомления о создании и изменении брони (Поправить тимлиду)

### 🛠️ Технологии
- Язык: Python 3.11
- Backend: FastAPI
- База данных: PostgreSQL + SQLAlchemy + Alembic
- Аутентификация: JWT
- Контейнеризация: Docker, Docker Compose
- Тестирование: Pytest
- CI/CD: GitHub Actions
- Инфраструктура: Nginx, Gunicorn/Uvicorn

### 📂 Структура проекта
```bash
.
├── alembic/                     # Миграции БД
│   ├── env.py
│   └── versions/
│       ├── 75a4c3ca3d56_init_schema.py
│       └── dd97e7701592_.py
│
├── infra/                       # Инфраструктура и деплой
│   ├── docker-compose.local.yml
│   ├── docker-compose.production.yml
│   ├── pgdata/                  # Данные PostgreSQL
│   └── requirements.txt
│
├── nginx/                       # Конфигурация Nginx
│   ├── local.conf
│   └── prod.conf
│
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
│   │
│   ├── crud/                    # CRUD-операции
│   │   ├── cafes.py
│   │   ├── dishes.py
│   │   ├── tables.py
│   │   ├── users.py
│   │   └── factory.py
│   │
│   ├── exceptions/              # Кастомные исключения
│   │   ├── auth.py
│   │   ├── db.py
│   │   └── user.py
│   │
│   ├── models/                  # SQLAlchemy-модели
│   │   ├── booking.py
│   │   ├── cafe.py
│   │   ├── dish.py
│   │   ├── table.py
│   │   └── user.py
│   │
│   ├── schemas/                 # Pydantic-схемы
│   │   ├── auth.py
│   │   ├── cafes.py
│   │   ├── dish.py
│   │   ├── table.py
│   │   ├── users.py
│   │   └── validators.py
│   │
│   ├── services/                # Бизнес-логика
│   │   ├── auth.py
│   │   └── slot_rules.py
│   │
│   └── main.py                  # Точка входа в приложение
│
├── tests/                       # Тесты Pytest
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_dishes.py
│   ├── test_tables.py
│   └── test_users.py
│
├── create_superuser_cli.py       # CLI-скрипт для создания суперпользователя
├── entrypoint.sh                 # Стартовый скрипт Docker
├── Dockerfile                    # Docker-образ для backend
├── requirements.txt              # Основные зависимости
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
### Настройка базы данных
- **Вариант A: SQLite (быстрый старт)**<br>
***В файле .env установите:***
```bash
DB_ENGINE=sqlite
```

- **Вариант B: PostgreSQL**<br>
***В файле .env установите:***
```
DB_ENGINE=postgresql
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=booking
DB_HOST=localhost
DB_PORT=5432
SECRET=your_secret_key_here
```
### Запуск приложения
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
| 🧪 **tests.yml** | Запускает тесты (pytest) и проверяет корректность кода | push, pull_request |
| 🧹 **style_check.yml** | Проверяет стиль кода (Ruff, Pre-commit) | push, pull_request |
| 📩 **telegram_notify.yml** | Отправляет уведомления о результатах в Telegram | после завершения других workflow |


**⚙️ Как это работает**<br>
- Разработчик делает push или pull request в репозиторий.
- GitHub Actions автоматически:
- собирает проект в Docker;
- прогоняет тесты;
- проверяет стиль кода;
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

### 🧪 Тестирование
**Запуск тестов локально с использованием базы данных SQLite**<br>
Из корня проекта выполнить команду:
```sh
python -m pytest
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
🧭 Станислав Баринов<br>

**Project Manager (PM):**<br>
📋 Александр Аваков<br>

**Тимлид:**<br>
🧑‍💻 Вадим Каримов<br>

**Разработчики:**<br>
💡 Вадим Каримов<br>
💡 Дмитрий Радюк<br>
💡 Александр Лавер<br>
💡 Игорь Могилин<br>
💡 Вика Долгова<br>
💡 Алексей Гасилин<br>
💡 Александр Комаров<br>
💡 Дмитрий Волков<br>
💡 Исхак Мурзаев<br>
💡 Михаил Яковенко<br>
