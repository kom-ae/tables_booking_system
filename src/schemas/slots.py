from __future__ import annotations

from datetime import datetime, time
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.constants import ID_MIN, SLOT_DESCRIPTION_MAX_LENGTH


class SlotBase(BaseModel):
    """Базовая схема слота.

    Принимает как is_active, так и active (alias), чтобы фронту было удобно.
    """

    model_config = ConfigDict(
        extra='forbid',
        populate_by_name=True,
    )

    cafe_id: int = Field(..., ge=ID_MIN, title='ID кафе')
    start_time: time = Field(..., title='Начало интервала')
    end_time: time = Field(..., title='Конец интервала')
    description: Optional[str] = Field(
        None,
        max_length=SLOT_DESCRIPTION_MAX_LENGTH,
        title='Описание',
    )
    is_active: bool = Field(
        True,
        title='Активен?',
        validation_alias='active',
        serialization_alias='active',
    )

    @model_validator(mode='after')
    def check_times(self) -> 'SlotBase':
        """Быстрая валидация: конец интервала должен быть позже начала."""
        if self.end_time <= self.start_time:
            raise ValueError('end_time должен быть позже start_time')
        return self


class SlotCreate(SlotBase):
    """Схема создания слота."""

    pass


class SlotUpdate(BaseModel):
    """Схема частичного обновления слота.

    Разрешены только перечисленные поля; None допустим,
    если поле не присылается вовсе.
    """

    model_config = ConfigDict(
        extra='forbid',
        populate_by_name=True,
    )

    cafe_id: Optional[int] = Field(None, ge=ID_MIN, title='ID кафе')
    start_time: Optional[time] = Field(None, title='Начало интервала')
    end_time: Optional[time] = Field(None, title='Конец интервала')
    description: Optional[str] = Field(
        None,
        max_length=SLOT_DESCRIPTION_MAX_LENGTH,
        title='Описание',
    )
    is_active: Optional[bool] = Field(
        None,
        title='Активен?',
        validation_alias='active',
        serialization_alias='active',
    )

    @model_validator(mode='after')
    def check_times(self) -> 'SlotUpdate':
        """Если оба времени присланы вместе — end_time > start_time.

        Если прислано только одно из времён — проверку сделает слой CRUD,
        собрав конечные значения вместе с текущим состоянием в БД.
        """
        if self.start_time is not None and self.end_time is not None:
            if self.end_time <= self.start_time:
                raise ValueError('end_time должен быть позже start_time')
        return self


class SlotDB(BaseModel):
    """Полная схема слота из БД (для ответов).

    Использует from_attributes=True, чтобы маппиться напрямую из ORM-модели.
    """

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: int
    cafe_id: int
    start_time: time
    end_time: time
    description: Optional[str] = None
    is_active: bool = Field(..., serialization_alias='active')
    created_at: datetime
    updated_at: Optional[datetime] = None


class SlotShortDB(BaseModel):
    """Короткая схема слота (для списков)."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: int
    cafe_id: int
    start_time: time
    end_time: time
    is_active: bool = Field(..., serialization_alias='active')
