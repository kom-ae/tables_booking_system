from enum import IntEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy import (
    Table as SA_Table,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.constants import MIN_GUESTS_NUMBER
from src.models.base import BaseModel

if TYPE_CHECKING:
    from src.models.cafe import Cafe
    from src.models.dish import Dishe
    from src.models.slot import Slot
    from src.models.table import Table
    from src.models.user import User


booking_table = SA_Table(
    'booking_table',
    BaseModel.metadata,
    Column('booking_id', ForeignKey('booking.id', ondelete='CASCADE'),
           primary_key=True),
    Column('table_id', ForeignKey('table.id', ondelete='CASCADE'),
           primary_key=True),
)

booking_slot = SA_Table(
    'booking_slot',
    BaseModel.metadata,
    Column('booking_id', ForeignKey('booking.id', ondelete='CASCADE'),
           primary_key=True),
    Column('slot_id', ForeignKey('time_slot.id', ondelete='CASCADE'),
           primary_key=True),
)

booking_dish = SA_Table(
    'booking_dish',
    BaseModel.metadata,
    Column('booking_id', ForeignKey('booking.id', ondelete='CASCADE'),
           primary_key=True),
    Column('dish_id', ForeignKey('dishe.id', ondelete='CASCADE'),
           primary_key=True),
)


class BookingStatus(IntEnum):
    """Статусы бронирования."""

    BOOKING = 0
    CANCELED = 1
    ACTIVE = 2


class Booking(BaseModel):
    """Модель бронирования."""

    __table_args__ = (
        CheckConstraint(
            f'guests_number >= {MIN_GUESTS_NUMBER}',
            name='check_guests_positive',
        ),
        CheckConstraint(
            f'status IN ({", ".join(str(s.value) for s in BookingStatus)})',
            name='check_booking_status_valid',
        ),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey('user.id'),
        nullable=False,
        index=True,
    )
    cafe_id: Mapped[int] = mapped_column(
        ForeignKey('cafe.id'),
        nullable=False,
        index=True,
    )
    guests_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    status: Mapped[int] = mapped_column(
        Integer,
        default=BookingStatus.BOOKING,
        nullable=False,
    )
    note: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    user: Mapped['User'] = relationship(lazy='selectin')
    cafe: Mapped['Cafe'] = relationship(lazy='selectin')
    tables: Mapped[list['Table']] = relationship(
        'Table',
        secondary='booking_table',
        lazy='selectin',
    )
    slots: Mapped[list['Slot']] = relationship(
        'Slot',
        secondary='booking_slot',
        lazy='selectin',
    )
    menu: Mapped[list['Dishe']] = relationship(
        'Dishe',
        secondary='booking_dish',
        lazy='selectin',
    )
