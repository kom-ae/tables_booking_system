from datetime import datetime

from pydantic import BaseModel


class BaseSchema(BaseModel):
    """Базовая схема."""

    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    active: bool = True

    class Config:
        """Конфиг класса."""

        orm_mode = True
