from typing import Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.constants import MAX_DESCRIPTION
from src.models.base import BaseModel
from src.models.cafe import Cafe


class Tables(BaseModel):
    """Модель столов."""

    __tablename__ = 'tables'

    cafe_id: Mapped[int] = mapped_column(
        ForeignKey('cafe.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    seats_number: Mapped[int] = mapped_column(
        Integer(),
        nullable=False,

    )
    description: Mapped[Optional[str]] = mapped_column(
        String(MAX_DESCRIPTION),
        nullable=True,
    )
    cafe: Mapped['Cafe'] = relationship(
        back_populates='tables',
        lazy='selectin',
    )
