import re

# -------------------
# JWT / Аутентификация
# -------------------
# Время жизни токена в секундах
JWT_LIFETIME_SECONDS = 1600

# Минимальный интервал обновления last_used
MIN_UPDATE_INTERVAL_SECONDS = 60

# -------------------
# Логирование Settings
# -------------------
MAX_BYTES_TEMP_LOGER = 1_000_000
BACKUP_COUNT_TEMP_LOGER = 3
LOG_FILE_APP_LOGGER = 'app.log'
LOG_FILE_TEMP_LOGER = 'app_temp.log'
DEFAULT_USER_ID = 0
SYSTEM_USERNAME = 'SYSTEM'

# -------------------
# Пользователи
# -------------------
USERNAME_MAX_LENGTH = 50
USERNAME_MIN_LENGTH = 3
EMAIL_MIN_LENGTH = 5
EMAIL_MAX_LENGTH = 255
PASSWORD_MAX_LENGTH = 128
PHONE_MAX_LENGTH = 15
TG_ID_MIN_LENGTH = 5
TG_ID_MAX_LENGTH = 15
ROLE_MAX_LENGTH = 10

# Регулярка для проверки международного формата телефона
PHONE_REGEX = re.compile(r'^\+7\d{10}$')  # +7XXXXXXXXXX

# Регулярка для проверки пароля
PASSWORD_REGEX = re.compile(
    r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,}$',
)

# Регулярка для проверки имени
USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_]+$')

# Регулярка для проверки email
EMAIL_REGEX = re.compile(r'^[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}$')

# Регулярка длоя проверки tg_id
TG_ID_REGEX = re.compile(r'^\d{5,15}$')


# -------------------
# Кафе / Бизнес
# -------------------
# Максимальная и минимальная длина телефона
MAX_TEL = 15
MIN_TEL = 5

# Максимальная и минимальная длина названия кафе
MAX_NAME_CAFE = 256
MIN_NAME_CAFE = 5

# Максимальная и минимальная длина адреса кафе
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
    # Допишите свои, если здесь их нет
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

# -------------------
# Slots
# -------------------

# Универсальный минимум для ID в роутах/схемах
ID_MIN = 1

SLOT_DESCRIPTION_MAX_LENGTH = 255
