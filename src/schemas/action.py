from datetime import datetime
from typing import Any, Optional, Type

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
)

from src.schemas.cafes import CafeShortDB


class ActionCreate(BaseModel):
    """Схема для создания акций."""

    cafe: int = Field(..., description='ID Кафе')
    description: str = Field(..., description='Описание акции', min_length=1)

    @field_validator('cafe', mode='before')
    @classmethod
    def set_cafe_id(
        cls: Type[Any],
        value: Any,
        info: ValidationInfo,
    ) -> Any:
        """Присваивает cafe_id из значения cafe."""
        if info.data:
            info.data['cafe_id'] = value
        return value


class ActionUpdate(ActionCreate):
    """Схема для изменения акций."""

    cafe: Optional[int] = Field(description='ID Кафе')
    description: Optional[str] = Field(description='Описание акции')
    is_active: Optional[bool] = Field(None, description='Объект активен?')


class ActionDB(BaseModel):
    """Возвращаемая схема акций."""

    id: int = Field(..., description='ID записи')
    cafe: CafeShortDB = Field(..., description='Кафе')
    description: str = Field(..., description='Описание акции')
    is_active: bool = Field(..., description='Объект активен?')
    created_at: datetime = Field(..., description='Дата создания')
    updated_at: datetime = Field(..., description='Дата обновления')

    model_config = ConfigDict(from_attributes=True)
