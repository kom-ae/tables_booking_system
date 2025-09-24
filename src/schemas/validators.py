from typing import Optional, Union

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


def cafe_update_field_is_not_null(
        cls,
        value: Union[str, bool, None]
        ) -> Union[str, bool]:
    """Проверка полей на null."""
    if value is None:
        raise ValueError('Поле не может быть null.')
    return value
