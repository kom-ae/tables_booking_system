from sqlalchemy import ForeignKey, Integer, String
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.constants import MAX_DESCRIPTION
from src.models.base import BaseModel
from src.models.cafes import Cafes


class Tables(BaseModel):
    """Модель столов."""

    __tablename__ = 'tables'

    cafe_id: Mapped[int] = mapped_column(
        ForeignKey('cafes.id', ondelete='CASCADE'),
        nullable=False,
    )
    seats_number: Mapped[int] = mapped_column(
        Integer(),
        nullable=False,

    )
    description: Mapped[Optional[str]] = mapped_column(
        String(MAX_DESCRIPTION),
        nullable=True,
    )
    cafe: Mapped['Cafes'] = relationship(
        'Cafes',
        back_populates='tables',
        )
