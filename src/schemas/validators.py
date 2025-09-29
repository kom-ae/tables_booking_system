from typing import Any, Optional

from src.constants import (
    EMAIL_MAX_LENGTH,
    EMAIL_MIN_LENGTH,
    EMAIL_REGEX,
    PASSWORD_REGEX,
    PHONE_REGEX,
    TG_ID_MAX_LENGTH,
    TG_ID_MIN_LENGTH,
    TG_ID_REGEX,
    USERNAME_MAX_LENGTH,
    USERNAME_MIN_LENGTH,
    USERNAME_REGEX,
)
from src.core.logger import logger
from src.exceptions.user import (
    AppException,
    InvalidEmailException,
    InvalidPasswordException,
    InvalidPhoneException,
    InvalidTelegramIDException,
    InvalidUsernameException,
)


def is_not_null(value: Any, field_name: str) -> str:
    """Проверяет, что значение не null и не пустая строка."""
    if value is None or (isinstance(value, str) and value.strip() == ''):
        raise AppException(f'Поле {field_name} не может быть пустым')
    return str(value).strip()


def phone_validator(value: Any, user: Optional[Any] = None) -> str:
    """Валидация телефона."""
    value = is_not_null(value, 'phone')
    if not PHONE_REGEX.match(value):
        logger.warning(f'Некорректный номер телефона: {value}', user=user)
        raise InvalidPhoneException(f'Некорректный номер телефона: {value}')
    logger.info(f'Телефон успешно прошёл проверку: {value}', user=user)
    return value


def username_validator(username: Any) -> str:
    """Валидация username."""
    username = is_not_null(username, 'username')
    if not (USERNAME_MIN_LENGTH <= len(username) <= USERNAME_MAX_LENGTH):
        raise InvalidUsernameException(
            f'Username должен быть от {USERNAME_MIN_LENGTH} '
            f'до {USERNAME_MAX_LENGTH} символов.',
        )
    if not USERNAME_REGEX.match(username):
        raise InvalidUsernameException(
            'Username может содержать только латинские буквы, цифры и _',
        )
    logger.info(f'Поле username: {username} прошло проверку')
    return username


def password_validator(password: Any, user: Optional[Any] = None) -> str:
    """Валидация пароля."""
    password = is_not_null(password, 'password')
    if not PASSWORD_REGEX.match(password):
        logger.warning(
            f'Пароль не соответствует требованиям безопасности: {password}',
            user=user,
        )
        raise InvalidPasswordException(
            'Пароль должен содержать минимум 8 символов, '
            'строчную и заглавную буквы, цифру и спецсимвол',
        )
    logger.info('Пароль успешно прошёл проверку', user=user)
    return password


def email_validator(email: Any, user: Optional[Any] = None) -> str:
    """Валидация email."""
    email_str = is_not_null(email, 'email')

    if not (EMAIL_MIN_LENGTH <= len(email_str) <= EMAIL_MAX_LENGTH):
        logger.warning(f'Некорректная длина email: {email_str}', user=user)
        raise InvalidEmailException(
            f'Email должен быть от {EMAIL_MIN_LENGTH} '
            f'до {EMAIL_MAX_LENGTH} символов.',
        )

    if not EMAIL_REGEX.match(email_str):
        logger.warning(f'Некорректный формат email: {email_str}', user=user)
        raise InvalidEmailException('Некорректный формат email адреса')

    logger.info(f'Email успешно прошёл проверку: {email_str}', user=user)
    return email_str


def telegram_id_validator(
    tg_id: Optional[Any],
    user: Optional[Any] = None,
) -> Optional[str]:
    """Валидация Telegram ID."""
    if tg_id is None:
        return None

    tg_id_str = is_not_null(tg_id, 'telegram_id')

    if not (TG_ID_MIN_LENGTH <= len(tg_id_str) <= TG_ID_MAX_LENGTH):
        logger.warning(
            f'Некорректная длина Telegram ID: {tg_id_str}',
            user=user,
        )
        raise InvalidTelegramIDException(
            f'Telegram ID должен быть от {TG_ID_MIN_LENGTH} '
            f'до {TG_ID_MAX_LENGTH} символов.',
        )

    if TG_ID_REGEX and not TG_ID_REGEX.match(tg_id_str):
        logger.warning(
            f'Некорректный формат Telegram ID: {tg_id_str}',
            user=user,
        )
        raise InvalidTelegramIDException(
            'Telegram ID может содержать только цифры и символ @',
        )

    logger.info(f'Telegram ID успешно прошёл проверку: {tg_id_str}', user=user)
    return tg_id_str


def cafe_update_field_is_not_null(value: Any) -> Any:
    """Проверка полей на null."""
    if value is None:
        raise ValueError('Поле не может быть null.')
    return value
