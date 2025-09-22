from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel
from src.models.cafes import Cafes


class Actions(BaseModel):
    """Модель акций."""

    description: Mapped[str] = mapped_column(Text, nullable=False)
    cafe_id: Mapped[int] = mapped_column(
        ForeignKey('cafes.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        )
    cafe: Mapped['Cafes'] = relationship(
        back_populates='actions',
        lazy='selectin',
    )
