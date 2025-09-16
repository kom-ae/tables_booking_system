from pydantic import BaseModel
from datetime import datetime


class BaseSchema(BaseModel):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    active: bool = True

    class Config:
        orm_mode = True
