from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.constants import (
    MAX_ADDRESS,
    MAX_NAME_CAFE,
    MAX_TEL,
    MIN_ADDRESS,
    MIN_NAME_CAFE,
    MIN_TEL,
)
from src.schemas.base import CafeBase
from src.schemas.validators import (
    cafe_update_field_is_not_null,
    phone_validator,
)


class CafeDB(CafeBase):
    """Возвращаемая схема кафе."""

    id: int = Field(..., title='ID записи')
    is_active: bool = Field(..., title='Объект активен?')
    created_at: datetime = Field(..., title='Дата создания')
    updated_at: datetime = Field(..., title='Дата обновления')


class CafeCreate(CafeBase):
    """Схема для создания кафе."""

    managers: Optional[list[int]] = Field([], title='ID менеджера')

    _validate_phone = field_validator('phone', mode='before')(phone_validator)


class CafeUpdate(BaseModel):
    """Схема для обновления кафе."""

    name: Optional[str] = Field(
        None,
        title='Название кафе',
        min_length=MIN_NAME_CAFE,
        max_length=MAX_NAME_CAFE,
    )
    address: Optional[str] = Field(
        None,
        title='Адрес кафе',
        min_length=MIN_ADDRESS,
        max_length=MAX_ADDRESS,
    )
    phone: Optional[str] = Field(
        None,
        title='Телефон кафе',
        min_length=MIN_TEL,
        max_length=MAX_TEL,
    )
    description: Optional[str] = Field(None, title='Описание кафе')
    photo: Optional[str] = Field(None, title='Фото кафе в формате base64')
    managers: Optional[list[int]] = Field([], title='ID менеджера')
    is_active: Optional[bool] = Field(None, title='Объект активен?')

    model_config = ConfigDict(extra='forbid')

    _validate_fields = field_validator(
        'name',
        'address',
        'phone',
        'is_active',
        'managers',
        'description',
        'photo',
        mode='before',
    )(cafe_update_field_is_not_null)

    _validate_phone = field_validator('phone', mode='before')(phone_validator)


class CafeShortDB(CafeBase):
    """Возвращаемая укороченная схема кафе."""

    id: int = Field(..., title='ID записи')
    is_active: bool = Field(..., title='Объект активен?')

    model_config = ConfigDict(from_attributes=True)
