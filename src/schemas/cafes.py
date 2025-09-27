from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from src.schemas.base import CafeBase
from src.schemas.validators import is_not_null, validate_active


class CafeDB(CafeBase):
    """Возвращаемая схема кафе."""

    id: int = Field(..., title='ID записи')
    is_active: bool = Field(..., title='Объект активен?')
    created_at: datetime = Field(..., title='Дата создания')
    updated_at: datetime = Field(..., title='Дата обновления')


class CafeCreate(CafeBase):
    """Схема для создания кафе."""

    managers: Optional[list[int]] = Field(None, title='ID менеджера')


class CafeUpdate(BaseModel):
    """Схема для обновления кафе."""

    name: Optional[str] = Field(None, description='Название кафе')
    address: Optional[str] = Field(None, description='Адрес кафе')
    phone: Optional[str] = Field(None, description='Телефон кафе')
    description: Optional[str] = Field(None, description='Описание кафе')
    photo: Optional[str] = Field(
        None,
        description='Фото кафе в формате base64',
    )
    managers: Optional[list[int]] = Field(None, description='ID менеджера')
    is_active: Optional[bool] = Field(None, description='Объект активен?')

    class Config:
        """Конфиг класса."""

        extra = 'forbid'

    _validate_name = field_validator('name', mode='before')(
        lambda value: is_not_null(value, 'name'),
    )
    _validate_address = field_validator('address', mode='before')(
        lambda value: is_not_null(value, 'address'),
    )
    _validate_phone = field_validator('phone', mode='before')(
        lambda value: is_not_null(value, 'phone'),
    )
    _validate_is_active = field_validator('is_active', mode='before')(
        validate_active,
    )


class CafeShortDB(CafeBase):
    """Возвращаемая укороченная схема кафе."""

    id: int = Field(..., title='ID записи')
    is_active: bool = Field(..., title='Объект активен?')
