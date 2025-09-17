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
        max_length=MAX_NAME_CAFE
    )
    address: str = Field(
        ...,
        title='Адрес кафе',
        min_length=1,
        max_length=MAX_ADDRESS
    )
    phone: str = Field(
        ...,
        title='Телефон кафе',
        min_length=1,
        max_length=MAX_TEL
    )
    description: Optional[str] = Field(None, title='Описание кафе')
    photo: Optional[str] = Field(None, title='Ссылка на фото кафе')
    managers: Optional[List[UserRead]] = Field(None)

    class Config:
        extra = 'forbid'


class CafeDB(CafeBase):
    """Возвращаемая схема кафе."""
    # В разработке


class CafeCreate(CafeBase):
    """Схема для создания кафе."""
    # В разработке


class CafeUpdate(CafeBase):
    """Схема для обновления кафе."""
    # В разработке


class CafeShortDB(CafeBase):
    """Возвращаемая укороченная схема кафе."""
    # В разработке
