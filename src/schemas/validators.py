import re
from typing import Optional

from src.api.exceptions.user import InvalidPhoneException
from src.constants import PHONE_REGEX


def phone_validator(v: Optional[str]) -> Optional[str]:
    """Проверка корректности телефона."""
    if v and not re.match(PHONE_REGEX, v):
        raise InvalidPhoneException(f'Некорректный номер телефона: {v}')
    return v
