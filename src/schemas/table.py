from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.constants import MAX_DESCRIPTION, MAX_SEATS_NUMBER, MIN_SEATS_NUMBER
from src.schemas.cafes import CafeShortDB


class TableBase(BaseModel):
    """Базовая схема для стола."""

    seats_number: int = Field(
        ...,
        ge=MIN_SEATS_NUMBER,
        le=MAX_SEATS_NUMBER,
        title='Количество мест',
    )
    description: Optional[str] = Field(
        None,
        max_length=MAX_DESCRIPTION,
        title='Описание столика',
    )

    model_config = ConfigDict(extra='forbid')


class TableCreate(TableBase):
    """Схема для создания стола."""

    is_active: bool = Field(True, title='Стол активен?')


class TableUpdate(BaseModel):
    """Схема для обновления стола."""

    seats_number: Optional[int] = Field(
        None,
        ge=MIN_SEATS_NUMBER,
        le=MAX_SEATS_NUMBER,
        title='Количество мест',
    )
    description: Optional[str] = Field(
        None,
        max_length=MAX_DESCRIPTION,
        title='Описание столика',
    )
    is_active: Optional[bool] = Field(None, title='Стол активен?')

    model_config = ConfigDict(extra='forbid')


class TableDB(TableBase):
    """Схема стола из БД."""

    id: int = Field(..., title='ID записи')
    cafe: CafeShortDB = Field(..., title='Кафе')
    is_active: bool = Field(..., title='Стол активен?')
    created_at: datetime = Field(..., title='Дата создания')
    updated_at: datetime = Field(..., title='Дата обновления')

    model_config = ConfigDict(from_attributes=True)


class TableShort(BaseModel):
    """Краткая схема стола."""

    id: int = Field(..., title='ID стола')
    seats_number: int = Field(..., title='Количество мест')
    is_active: bool = Field(..., title='Активен?')
    description: Optional[str] = Field(None, title='Описание')

    model_config = ConfigDict(from_attributes=True)
