import re

# -------------------
# JWT / Аутентификация
# -------------------
# Время жизни токена в секундах
JWT_LIFETIME_SECONDS = 1600

# Минимальный интервал обновления last_used
MIN_UPDATE_INTERVAL_SECONDS = 60


# -------------------
# User model constraints
# -------------------
USERNAME_MAX_LENGTH = 255
EMAIL_MAX_LENGTH = 255
PASSWORD_MAX_LENGTH = 128
PHONE_MAX_LENGTH = 20
TG_ID_MAX_LENGTH = 50
ROLE_MAX_LENGTH = 50

# -------------------
# Логирование Settings
# -------------------
MAX_BYTES_TEMP_LOGER = 1000000
BACKUP_COUNT_TEMP_LOGER = 3
LOG_FILE_TEMP_LOGER = 'app_temp.log'

# -------------------
# Пользователи
# -------------------
# Минимальная длина пароля
MIN_LENGTH_PASSWORD = 8

# Минимальная длина username
MIN_LENGTH_USERNAME = 1

# Максимальная длина username
MAX_LENGTH_USERNAME = 40

# Регулярка для проверки международного формата телефона
PHONE_REGEX = re.compile(
    r'^(\+[1-9]\d{0,2})\d{6,15}$',  # +код страны, затем 6-15 цифр
)

# Регулярка для проверки пароля
PASSWORD_REGEX = re.compile(
    r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^a-zA-Z0-9]).{8,}$',
    # Минимум: 1 заглавная, 1 строчная, 1 цифра, 1 спецсимвол, длина ≥8
)

# -------------------
# Кафе / Бизнес
# -------------------
# Максимальная и минимальная длинна телефона
MAX_TEL = 15
MIN_TEL = 5

# Максимальная и минимальная длина названия кафе
MAX_NAME_CAFE = 256
MIN_NAME_CAFE = 5

# Максимальная и минимальная длинна адреса кафе
MAX_ADDRESS = 256
MIN_ADDRESS = 5

# Описание тэгов
TAGS_METADATA = [
    {
        'name': 'Аутентификация',
        'description': 'Аутентификация пользователя',
    },
    {
        'name': 'Пользователи',
        'description': 'Управление пользователями сервиса',
    },
    {
        'name': 'Кафе',
        'description': 'Управление кафе',
    },
    {
        'name': 'Столы',
        'description': 'Управление столами',
    },
    {
        'name': 'Временные слоты',
        'description': 'Управление временными слотами',
    },
    # Допишите свои если здесь их нет
]


# -------------------
# Блюда
# -------------------
# Максимальная длина названия блюда
MAX_DISH_LENGTH_NAME = 200
# Максимальная длина описания блюда
MAX_DISH_LENGTH_DESC = 600
# Значение Numeric для цены блюда
DISH_PRICE_PRECISION = (10, 2)

# -------------------
# Столы
# -------------------
# Максимальная длина description для модели Tables
MAX_DESCRIPTION = 256

# Минимальное количество мест стола
MIN_SEATS_NUMBER = 1

# Максимальное количество мест стола
MAX_SEATS_NUMBER = 12

# Минимальное знаение id кафе
MIN_ID_CAFE = 1
