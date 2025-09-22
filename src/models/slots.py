from datetime import time
from typing import Optional

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import BaseModel


class Slots(BaseModel):
    """Интервал бронирования в рамках конкретного кафе."""

    __tablename__ = "slots"

    cafe_id: Mapped[int] = mapped_column(
        ForeignKey("cafes.id", ondelete="CASCADE"), index=True, nullable=False
    )
    start_time: Mapped[time] = mapped_column(nullable=False)
    end_time: Mapped[time] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), default=None)

    cafe = relationship("Cafes", back_populates="slots")

    __table_args__ = (
        UniqueConstraint("cafe_id", "start_time", "end_time",
                         name="uq_cafe_time_window"),
    )
