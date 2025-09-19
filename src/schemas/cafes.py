from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

from src.constants import MAX_ADDRESS, MAX_NAME_CAFE, MAX_TEL, MIN_TEL, MIN_ADDRESS, MIN_NAME_CAFE
from src.schemas.user import UserRead


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
    photo: Optional[str] = Field(None, title='Ссылка на фото кафе')
    managers: Optional[List[UserRead]] = Field(None)

    class Config:
        """Конфиг класса."""

        extra = 'forbid'


class CafeDB(CafeBase):
    """Возвращаемая схема кафе."""

    id: int = Field(..., title='ID записи')
    active: bool = Field(..., title='Объект активен?')
    created_at: datetime = Field(..., title='Дата создания')
    updated_at: datetime = Field(..., title='Дата обновления')

    class Config:
        """Конфиг класса."""

        from_attributes = True


class CafeCreate(CafeBase):
    """Схема для создания кафе."""


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
    photo: Optional[str] = Field(None, title='Ссылка на фото кафе')
    managers: Optional[List[UserRead]] = Field(None)
    active: Optional[bool] = Field(None, title='Объект активен?')

    class Config:
        """Конфиг класса."""

        extra = 'forbid'

# Проверить работу валидатора
    @field_validator('name', 'address', 'phone', 'active', mode='before')
    @classmethod
    def is_not_null(cls, value: Optional[str]) -> str:
        """Проверка полей на null."""
        if value is None:
            raise ValueError(
                'Поля name, address, phone, active не могут быть null.')
        return value


class CafeShortDB(CafeBase):
    """Возвращаемая укороченная схема кафе."""

    id: int = Field(..., title='ID записи')
    active: bool = Field(..., title='Объект активен?')

    class Config:
        """Конфиг класса."""

        from_attributes = True
