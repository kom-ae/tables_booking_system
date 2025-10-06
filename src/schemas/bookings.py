from datetime import datetime
from enum import IntEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from src.constants import MIN_GUESTS_NUMBER
from src.schemas.base import BaseSchema
from src.schemas.cafes import CafeShortDB
from src.schemas.dish import Dish
from src.schemas.slots import SlotShortDB
from src.schemas.table import TableShort
from src.schemas.users import UserShort

BOOKING_STATUS_SCHEMA = {
    'oneOf': [
        {'const': 0, 'title': 'booking', 'description': 'Забронировано'},
        {'const': 1, 'title': 'canceled', 'description': 'Отменено'},
        {'const': 2, 'title': 'active', 'description': 'Клиент подошел'},
    ],
}


class BookingStatus(IntEnum):
    """Статусы бронирования."""

    BOOKING = 0
    CANCELED = 1
    ACTIVE = 2


class BookingBase(BaseModel):
    """Базовая схема бронирования."""

    guests_number: int = Field(..., ge=MIN_GUESTS_NUMBER,
                               description='Количество гостей')
    note: Optional[str] = Field(None, description='Комментарий к бронированию')

    model_config = ConfigDict(extra='forbid')


class BookingCreate(BookingBase):
    """Схема для создания бронирования."""

    user_id: int = Field(..., description='ID пользователя')
    cafe_id: int = Field(..., description='ID кафе')
    tables: list[int] = Field(..., description='Бронируемые столы')
    slots: list[int] = Field(..., description='Слоты бронирования')
    menu: Optional[list[int]] = Field(
        default_factory=list,
        description='Блюда для предварительного заказа',
    )


class BookingUpdate(BookingBase):
    """Схема для обновления бронирования."""

    guests_number: Optional[int] = Field(None, description='Количество гостей')
    tables: Optional[list[int]] = Field(None, description='Бронируемые столы')
    slots: Optional[list[int]] = Field(None, description='Слоты бронирования')
    menu: Optional[list[int]] = Field(
        None,
        description='Блюда для предварительного заказа',
    )
    status: Optional[BookingStatus] = Field(
        None,
        description='Статус бронирования',
        json_schema_extra=BOOKING_STATUS_SCHEMA,
    )
    is_active: Optional[bool] = Field(None, description='Объект активен?')

    model_config = ConfigDict(extra='forbid')


class Booking(BookingBase, BaseSchema):
    """Схема бронирования из БД."""

    id: int = Field(..., description='ID записи')
    user: UserShort = Field(..., description='Пользователь')
    cafe: CafeShortDB = Field(..., description='Кафе')
    tables: list[TableShort] = Field(..., description='Забронированные столы')
    slots: list[SlotShortDB] = Field(..., description='Время бронирования')
    menu: Optional[list[Dish]] = Field(
        default_factory=list,
        description='Блюда для предварительного заказа',
    )
    status: BookingStatus = Field(
        ...,
        description='Статус бронирования',
        json_schema_extra=BOOKING_STATUS_SCHEMA,
    )
    is_active: bool = Field(..., description='Объект активен?')
    created_at: datetime = Field(..., description='Дата создания')
    updated_at: datetime = Field(..., description='Дата обновления')

    model_config = ConfigDict(from_attributes=True)
