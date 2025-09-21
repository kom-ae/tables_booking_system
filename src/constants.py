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
PASSWORD_MAX_LENGTH = 255
PHONE_MAX_LENGTH = 20
TG_ID_MAX_LENGTH = 50
ROLE_MAX_LENGTH = 50
DEFAULT_LAST_USED = 0.0
DEFAULT_ROLE = 'user'


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
PHONE_REGEX = r'^(\+[1-9]\d{0,2})\d{6,15}$'

# Регулярка для проверки пароля
PASSWORD_REGEX = re.compile(
    r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[^a-zA-Z0-9]).{8,}$',
)

# -------------------
# Кафе / Бизнес
# -------------------
# Максимальная длина телефонного номера
MAX_TEL = 256

# Максимальная длина названия кафе
MAX_NAME_CAFE = 256

# Максимальная длина адреса кафе
MAX_ADDRESS = 256

# -------------------
# Логирование
# -------------------

# Дефолтное значение user_id для системных операций
ZERO_DEFAULT_USER_ID = 0

# Имя файла для логов
LOG_FILE = 'app.log'

# Максимальный размер файла логов (5 MB)
MAX_BYTES = 5 * 1024 * 1024  # 5 MB

# Количество ротационных файлов логов
BACKUP_COUNT = 3

# Имя системного пользователя для логирования действий без конкретного юзера
SYSTEM_USERNAME = 'SYSTEM'
