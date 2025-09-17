from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from src.constants import MAX_ADDRESS, MAX_NAME_CAFE, MAX_TEL
from src.schemas.user import UserRead


class CafeBase(BaseModel):
    """Базовая схема для кафе."""

    name: str = Field(
        ...,
        title='Название кафе',
        min_length=1,
        max_length=MAX_NAME_CAFE,
    )
    address: str = Field(
        ...,
        title='Адрес кафе',
        min_length=1,
        max_length=MAX_ADDRESS,
    )
    phone: str = Field(
        ...,
        title='Телефон кафе',
        min_length=1,
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
    created_at: datetime = Field(..., 'Дата создания')
    updated_at: datetime = Field(..., 'Дата обновления')

    class Config:
        """Конфиг класса."""

        orm_mode = True


class CafeCreate(CafeBase):
    """Схема для создания кафе."""


class CafeUpdate(BaseModel):
    """Схема для обновления кафе."""

    name: Optional[str] = Field(
        None,
        title='Название кафе',
        min_length=1,
        max_length=MAX_NAME_CAFE,
    )
    address: Optional[str] = Field(
        None,
        title='Адрес кафе',
        min_length=1,
        max_length=MAX_ADDRESS,
    )
    phone: Optional[str] = Field(
        None,
        title='Телефон кафе',
        min_length=1,
        max_length=MAX_TEL,
    )
    description: Optional[str] = Field(None, title='Описание кафе')
    photo: Optional[str] = Field(None, title='Ссылка на фото кафе')
    managers: Optional[List[UserRead]] = Field(None)
    active: Optional[bool] = Field(None, title='Объект активен?')

    class Config:
        """Конфиг класса."""

        extra = 'forbid'


class CafeShortDB(CafeBase):
    """Возвращаемая укороченная схема кафе."""

    id: int = Field(..., title='ID записи')
    active: bool = Field(..., title='Объект активен?')

    class Config:
        """Конфиг класса."""

        orm_mode = True
