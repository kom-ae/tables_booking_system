from datetime import datetime

from pydantic import BaseModel


class BaseSchema(BaseModel):
    """Базовый класс для схем."""

    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    active: bool = True

    class Config:
        """Класс настройки поведения модели."""

        orm_mode = True
