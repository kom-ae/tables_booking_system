from typing import Optional

from src.constants import PASSWORD_REGEX, PHONE_REGEX
from src.core.logger import project_log
from src.exceptions.user import InvalidPasswordException, InvalidPhoneException


def phone_validator(
    value: Optional[str],
    user: Optional[object] = None,
) -> Optional[str]:
    """Проверка корректности телефона."""
    if value and not PHONE_REGEX.match(value):
        project_log(
            'warning',
            f'Некорректный номер телефона: {value}',
            user=user,
        )
        raise InvalidPhoneException(f'Некорректный номер телефона: {value}')

    project_log(
        'info',
        f'Телефон успешно прошёл проверку: {value}',
        user=user,
    )
    return value


def password_validator(password: str, user: Optional[object] = None) -> str:
    """Валидация пароля."""
    if not PASSWORD_REGEX.match(password):
        project_log(
            'warning',
            f'Пароль не соответствует требованиям безопасности: {password}',
            user=user,
        )
        raise InvalidPasswordException(
            'Пароль должен содержать минимум 8 символов, '
            'строчную и заглавную буквы, цифру и спецсимвол',
        )

    project_log(
        'info',
        'Пароль успешно прошёл проверку',
        user=user,
    )
    return password


def is_not_null(value: Optional[str], field_name: str) -> str:
    """Проверка полей на null."""
    if value is None:
        raise ValueError(f'Поле {field_name} не может быть null.')
    return value


def validate_active(value: Optional[bool]) -> Optional[bool]:
    """Проверка поля is_active."""
    if value is None:
        raise ValueError('Поле is_active не может быть null.')
    return value
