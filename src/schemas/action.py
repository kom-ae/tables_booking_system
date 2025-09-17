from typing import Optional

from pydantic import BaseModel

from src.schemas.base import BaseSchema


class ActionsBase(BaseSchema):
    cafe: Optional[dict] = None
    description: str


class ActionsCreate(BaseModel):
    pass


class ActionsUpdate(ActionsCreate):
    pass


class ActionsDB(ActionsBase, BaseSchema):
    pass
