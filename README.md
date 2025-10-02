## 🍽 Tables Booking System
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
tables_booking_system_team2/
│── src/                  # Основной код приложения
│   ├── api/              # Роутеры FastAPI
│   ├── core/             # Настройки и конфигурации
│   ├── crud/             # Логика работы с БД
│   ├── models/           # SQLAlchemy-модели
│   ├── schemas/          # Pydantic-схемы
│   ├── services/         # Бизнес-логика
│   └── main.py           # Точка входа
│
│── tests/                # Тесты
│── infra/                # Docker и деплой
│── alembic/              # Миграции БД
│── nginx/                # Конфигурация nginx
│── requirements.txt      # Зависимости
│── docker-compose.yml    # Docker Compose
│── README.md             # Документация
```
### ⚙️ Установка и запуск

### Для локальной разработки

***Клонирование репозитория***
```bash
git clone https://github.com/Studio-Yandex-Practicum/tables_booking_system_team2.git
cd tables_booking_system_team2
```
### Настройка окружения
***Копируем файл окружения***
```bash
cd src
cp env.local .env
```
### Настройка базы данных
 - ***Вариант A: SQLite (быстрый старт)***
```bash
# В файле .env установите:
DB_ENGINE=sqlite
DATABASE_URL=sqlite+aiosqlite:///./booking.db
```
- ***Вариант B: PostgreSQL (продакшен-готовый)***<br>
***В файле .env установите:***
```
DB_ENGINE=postgresql
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=booking
DB_HOST=localhost
DB_PORT=5432
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/booking
SECRET_KEY=your_secret_key_here
```
### Запуск приложения
**С Docker (рекомендуется)**<br>
***Копируем .env в директорию infra***
```bash
cp .env infra/.env
```
### Запускаем контейнеры
```bash
cd src/infra
docker-compose -f docker-compose.local.yml up --build
```
**Без Docker**<br>
***Создание виртуального окружения***
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
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```
### Проверка работоспособности
***После запуска приложение будет доступно:***
- API: http://localhost:8000
- Документация: http://localhost:8000/docs
- Альтернативная документация: http://localhost:8000/redoc<br>

### Переменные окружения (.env)
 ***Для PostgreSQL:***
 ```bash
 POSTGRES_USER=postgres
 POSTGRES_PASSWORD=postgres
 POSTGRES_DB=booking
 DB_HOST=localhost
 DB_PORT=5432
 ```
 ***Для SQLite:***
 ```bash
 DATABASE_URL=sqlite+aiosqlite:///./booking.db
 ```
**Приложение будет доступно по адресу:**<br>
👉 http://localhost/api/v1

**Документация API:**<br>
👉 http://localhost/docs

### 🔄 CI/CD
(Дополнить)

### 🧪 Тестирование
***Запуск тестов локально с использованием базы данных SQLite***
```sh
cd src
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

***Проверка стиля***
```sh
ruff check
```
***Проверка и автофикс***
```sh
ruff check --fix
```
***Автоматическая проверка при коммитах.***<br>
Чтобы при каждом коммите автоматически проверялась и исправлялась стилистика, нужно подключить pre-commit:
```sh
pre-commit install
```

### 👥 Команда разработки
Проект выполнен в рамках обучения в Яндекс Практикуме.
(ДОПОЛНИТЬ)
.....

📌 Roadmap
 - Подключить Telegram-бота для уведомлений
 - Добавить интеграцию с оплатой
 - Реализовать модуль рекомендации столиков
