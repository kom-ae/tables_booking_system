from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from src.constants import (
    MAX_ADDRESS,
    MAX_NAME_CAFE,
    MAX_TEL,
    MIN_ADDRESS,
    MIN_NAME_CAFE,
    MIN_TEL,
)
from src.schemas.users import UserShort


class BaseSchema(BaseModel):
    """Базовая схема с общими полями для всех моделей."""

    id: Optional[int] = Field(None, description='ID')
    created_at: Optional[datetime] = Field(None, description='Дата создания')
    updated_at: Optional[datetime] = Field(None, description='Дата обновления')
    is_active: bool = Field(None, description='Активен ли пользователь.')


class CafeBase(BaseModel):
    """Базовая схема для кафе."""

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
    managers: Optional[list[UserShort]] = Field(None, title='ID менеджера')

    class Config:
        """Конфиг класса."""

        extra = 'forbid'


class Error(BaseModel):
    """Схема ошибки."""

    message: str
