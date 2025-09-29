from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BaseSchema(BaseModel):
    """Базовая схема с общими полями для всех моделей."""

    id: Optional[int] = Field(None, description='ID')
    created_at: Optional[datetime] = Field(None, description='Дата создания')
    updated_at: Optional[datetime] = Field(None, description='Дата обновления')
    is_active: bool = Field(None, description='Активен ли пользователь.')


class Error(BaseModel):
    """Схема ошибки."""

    message: str
