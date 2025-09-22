from datetime import time, datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator
from pydantic.config import ConfigDict

from src.schemas.base import BaseSchema


class SlotBase(BaseModel):
    """Базовая схема слота (вход/базовые поля)."""
    model_config = ConfigDict(extra='forbid')

    cafe_id: int = Field(..., ge=1, title='ID кафе')
    start_time: time = Field(..., title='Начало интервала')
    end_time: time = Field(..., title='Конец интервала')
    description: Optional[str] = Field(None, max_length=255, title='Описание')
    is_active: bool = Field(True, title='Активен?')

    @model_validator(mode="after")
    def check_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time должен быть позже start_time")
        return self


class SlotCreate(SlotBase):
    """Схема создания слота."""
    pass


class SlotUpdate(BaseModel):
    """Схема частичного обновления слота."""

    model_config = ConfigDict(extra='forbid')
    start_time: Optional[time] = Field(None, title='Начало интервала')
    end_time: Optional[time] = Field(None, title='Конец интервала')
    description: Optional[str] = Field(None, max_length=255, title='Описание')
    is_active: Optional[bool] = Field(None, title='Активен?')

    @model_validator(mode="after")
    def check_times(self):
        if self.start_time is not None and self.end_time is not None:
            if self.end_time <= self.start_time:
                raise ValueError("end_time должен быть позже start_time")
        return self


class SlotDB(SlotBase, BaseSchema):
    """Возвращаемая схема слота (из БД)."""

    is_active: bool = Field(..., serialization_alias='active')
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class SlotShortDB(BaseModel):
    """Укороченная схема для списков, если нужна."""
    model_config = ConfigDict(from_attributes=True, extra='forbid')

    id: int
    cafe_id: int
    start_time: time
    end_time: time
    is_active: bool = Field(..., serialization_alias='active')
