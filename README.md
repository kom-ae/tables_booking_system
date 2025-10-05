# 🍽 Tables Booking System
Tables Booking System — это веб-приложение для онлайн-бронирования столиков в ресторанах.
Система позволяет пользователям искать свободные столики, бронировать их на удобное время, а администраторам — управлять заведением и бронированиями.

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
├── alembic/                  # Миграции базы данных
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   └── versions/
│
├── infra/                    # Инфраструктура и докер
│   ├── docker-compose.local.yml
│   ├── docker-compose.production.yml
│   ├── docker-compose.prod.yml.bac
│   └── requirements.txt
│
├── logs/                     # Логи приложения
│   └── app.log
│
├── nginx/                    # Конфигурация Nginx
│   ├── local.conf
│   └── prod.conf
│
├── src/                          # Исходный код приложения
│   ├── api/                      # Роуты (FastAPI endpoints)
│   ├── constants.py
│   ├── core/                     # Настройки, логгер, зависимости
│   ├── crud/                     # CRUD-операции
│   ├── exceptions/               # Кастомные исключения
│   ├── models/                   # SQLAlchemy модели
│   ├── schemas/                  # Pydantic-схемы
│   ├── services/                 # Бизнес-логика
│   ├── main.py                   # Точка входа FastAPI
│   ├── Dockerfile.local          # Dockerfile для локалки
│   ├── Dockerfile.prod           # Dockerfile для продакшена
│   ├── create_superuser_cli.py   # Скрипт создания суперюзера на проде
│   └── AuthJWT.md                # Документация по Auth/JWT
└── requirements.txt              # Зависимости для src
│
├── tests/                        # Тесты (pytest)
│   ├── test_actions.py
│   ├── test_auth.py
│   ├── test_bookings.py
│   ├── test_cafes.py
│   ├── test_dishes.py
│   ├── test_integration.py
│   ├── test_tables.py
│   ├── test_time_slots.py
│   └── test_users.py
│
├── alembic.ini               # Конфиг Alembic
├── Dockerfile                # Dockerfile для корневого уровня
├── entrypoint.sh             # Скрипт запуска
├── env.local                 # Переменные окружения (локально)
├── env.prod                  # Переменные окружения (продакшн)
├── fastapi.db                # SQLite база (для отладки)
├── pytest.ini                # Конфиг Pytest
├── requirements.txt          # Общие зависимости
├── requirements_style.txt    # Зависимости для линтеров/стиля
├── ruff.toml                 # Конфиг линтера Ruff
├── README.md                 # Документация
└── venv/
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
cp env.local .env
```
### Настройка базы данных
- **Вариант A: SQLite (быстрый старт)**<br>
***В файле .env установите:***
```bash
DB_ENGINE=sqlite
```
- **Вариант B: PostgreSQL (продакшен-готовый)**<br>
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
uvicorn src.main:app --reload --port 8000

```
### Проверка работоспособности
**После запуска приложение будет доступно:**
- API: http://localhost:8000
- Документация: http://localhost:8000/docs
- Альтернативная документация: http://localhost:8000/redoc<br>

### Переменные окружения (.env)
 ***Для PostgreSQL:***
 ```bash
 DB_ENGINE=postgres
 POSTGRES_USER=postgres
 POSTGRES_PASSWORD=postgres
 POSTGRES_DB=booking
 DB_HOST=localhost
 DB_PORT=5432
 ```
 ***Для SQLite:***
 ```bash
DB_ENGINE=sqlite
 ```
**Приложение будет доступно по адресу:**<br>
👉 http://localhost/api/v1

**Документация API:**<br>
👉 Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)<br>
👉 ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 🔄 CI/CD
**⚙️ Развертывание и автоматизация проекта выполнены через GitHub Actions.**<br>
Каждый коммит, push или pull request автоматически проверяется, тестируется и сопровождается уведомлением в Telegram.

**🚀 Основные процессы CI/CD**<br>
- 🧪 tests.yml	Запускает тесты (pytest) и проверяет корректность кода	push, pull_request
- 🧹 style_check.yml	Проверяет стиль кода (Ruff, Pre-commit)	push, pull_request
- 📨 telegram_notify.yml	Отправляет результаты выполнения workflow в Telegram<br>
	   после завершения других workflow

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
**Проект создан в рамках обучения в Яндекс Практикуме.**
```bash
Наставник:
🧭 Станислав Баринов
Project Manager (PM):
📋 Александр Аваков
Тимлид:
🧑‍💻 Вадим Каримов
Разработчики:
💡 Вадим Каримов
💡 Дмитрий Радюк
💡 Александр Лавер
💡 Игорь Могилин
💡 Вика Долгова
💡 Алексей Гасилин
💡 Дмитрий Волков
💡 Исхак Мурзаев
💡 Михаил Яковенко
💡 Александр Комаров
```
