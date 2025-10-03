from __future__ import annotations

from datetime import datetime, time
from typing import Optional, Self

from pydantic import (
    BaseModel, ConfigDict, Field, model_validator, field_validator)

from src.constants import SLOT_DESCRIPTION_MAX_LENGTH
from src.schemas.cafes import CafeShortDB


class SlotBase(BaseModel):
    """Базовая схема слота."""

    model_config = ConfigDict(extra='forbid')

    start_time: time
    end_time: time
    description: Optional[str] = Field(
        None,
        max_length=SLOT_DESCRIPTION_MAX_LENGTH,
    )
    is_active: bool = True

    @model_validator(mode='after')
    def check_times(self) -> SlotBase:
        """Проверяет, что end_time позже start_time."""
        if self.end_time <= self.start_time:
            raise ValueError('end_time должен быть позже start_time')
        return self


class SlotCreate(BaseModel):

    date: date = Field(..., examples=['2025-10-05'])
    start_time: time = Field(..., examples=['10:00:00'])
    end_time: time = Field(..., examples=['12:00:00'])
    description: Optional[str] = Field(None, examples=['Утренний слот'])
    is_active: bool = True

    @field_validator('end_time')
    @classmethod
    def _end_after_start(cls, v: time, info):
        start = info.data.get('start_time')
        if start and v <= start:
            raise ValueError('end_time должен быть позже start_time')
        return v

    model_config = ConfigDict(from_attributes=True)


class SlotUpdate(BaseModel):
    """Частичное обновление слота."""

    model_config = ConfigDict(extra='forbid')

    date: Optional[date] = Field(None, examples=['2025-10-06'])
    start_time: Optional[time] = Field(None, examples=['11:00:00'])
    end_time: Optional[time] = Field(None, examples=['13:00:00'])
    description: Optional[str] = None
    is_active: Optional[bool] = None

    @model_validator(mode='after')
    def check_times(self) -> Self:
        """Если заданы оба времени, end_time должен быть позже start_time."""
        if self.start_time is not None and self.end_time is not None:
            if self.end_time <= self.start_time:
                raise ValueError('end_time должен быть позже start_time')
        return self


class SlotDB(BaseModel):
    """Слот из БД."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    cafe: CafeShortDB
    start_time: time
    end_time: time
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SlotShortDB(BaseModel):
    """Короткая версия слота."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    cafe: CafeShortDB
    start_time: time
    end_time: time
    is_active: bool
