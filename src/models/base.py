from sqlalchemy import Column, Integer, DateTime, Boolean, func
from src.core.db import Base


class BaseModel(Base):
    __abstract__ = True
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    active = Column(Boolean, default=True)
