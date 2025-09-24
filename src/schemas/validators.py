from typing import Optional

from src.constants import PASSWORD_REGEX, PHONE_REGEX
from src.exceptions.user import InvalidPhoneException


def phone_validator(value: Optional[str]) -> Optional[str]:
    """Проверка корректности телефона."""
    if value and not PHONE_REGEX.match(value):
        raise InvalidPhoneException(f'Некорректный номер телефона: {value}')
    return value


def password_validator(password: str) -> str:
    """Валидация пароля."""
    if not PASSWORD_REGEX.match(password):
        raise ValueError(
            'Пароль должен содержать минимум 8 символов, '
            'строчную и заглавную буквы, цифру и спецсимвол',
        )
    return password


def cafe_update_field_is_not_null(cls, value: Optional[str]) -> str:
    """Проверка полей на null."""
    if value is None:
        raise ValueError(
            'Поля name, address, phone, is_active не могут быть null.',
        )
    return value
