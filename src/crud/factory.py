from src.crud.user import CRUDUser
from src.crud.slots import CRUDSlot

from src.models.user import User
from src.models.slots import Slots


def get_user_crud() -> CRUDUser:
    """Возвращает CRUD для модели User."""
    return CRUDUser(User)


def get_slot_crud() -> CRUDSlot:
    """Возвращает CRUD для модели Slots."""
    return CRUDSlot(Slots)
