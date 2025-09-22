from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from src.constants import (
    MAX_ADDRESS,
    MAX_NAME_CAFE,
    MAX_TEL,
    MIN_ADDRESS,
    MIN_NAME_CAFE,
    MIN_TEL,
)
from src.schemas.users import UserShort
from src.schemas.validators import (
    cafe_update_field_is_not_null,
    phone_validator,
)


class CafeBase(BaseModel):
    """Базовая схема для кафе."""

    id: int = Field(..., description='ID записи')
    name: str = Field(
        ...,
        title='Название кафе',
        min_length=MIN_NAME_CAFE,
        max_length=MAX_NAME_CAFE,
    )
    address: str = Field(
        ...,
        title='Адрес кафе',
        min_length=MIN_ADDRESS,
        max_length=MAX_ADDRESS,
    )
    phone: str = Field(
        ...,
        title='Телефон кафе',
        min_length=MIN_TEL,
        max_length=MAX_TEL,
    )
    description: Optional[str] = Field(None, title='Описание кафе')
    photo: Optional[str] = Field(None, title='Фото кафе в формате base64')
    managers: Optional[List[UserShort]] = Field(None, title='ID менеджера')

    class Config:
        """Конфиг класса."""

        extra = 'forbid'


class Cafe(CafeBase):
    """Возвращаемая схема кафе."""

    id: int = Field(..., title='ID записи')
    is_active: bool = Field(..., title='Объект активен?')
    created_at: datetime = Field(..., title='Дата создания')
    updated_at: datetime = Field(..., title='Дата обновления')

    class Config:
        """Конфиг класса."""

        from_attributes = True


class CafeCreate(BaseModel):
    """Схема для создания кафе."""

    managers: Optional[List[int]] = Field([], title='ID менеджера')

    _validate_phone = field_validator('phone', mode='before')(phone_validator)


class CafeUpdate(BaseModel):
    """Схема для обновления кафе."""

    name: str = Field(
        None,
        title='Название кафе',
        min_length=MIN_NAME_CAFE,
        max_length=MAX_NAME_CAFE,
    )
    address: str = Field(
        None,
        title='Адрес кафе',
        min_length=MIN_ADDRESS,
        max_length=MAX_ADDRESS,
    )
    phone: str = Field(
        None,
        title='Телефон кафе',
        min_length=MIN_TEL,
        max_length=MAX_TEL,
    )
    description: Optional[str] = Field(None, title='Описание кафе')
    photo: Optional[str] = Field(None, title='Фото кафе в формате base64')
    managers: Optional[List[int]] = Field([], title='ID менеджера')
    is_active: Optional[bool] = Field(None, title='Объект активен?')

    class Config:
        """Конфиг класса."""

        extra = 'forbid'

    # Проверить работу валидатора
    _validate_fields = field_validator(
        'name',
        'address',
        'phone',
        'is_active',
        'managers',
        mode='before',
    )(cafe_update_field_is_not_null)

    _validate_phone = field_validator('phone', mode='before')(phone_validator)


class CafeShortDB(CafeBase):
    """Возвращаемая укороченная схема кафе."""

    id: int = Field(..., title='ID записи')
    is_active: bool = Field(..., title='Объект активен?')

    class Config:
        """Конфиг класса."""

        from_attributes = True
