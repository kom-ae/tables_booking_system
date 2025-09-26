from src.crud.cafes import CRUDCafe
from src.crud.users import CRUDUser
from src.crud.slots import CRUDSlot
from src.models import Cafes, User, Slots


def get_user_crud() -> CRUDUser:
    """Возвращает CRUD для модели User."""
    return CRUDUser(User)


def get_cafe_crud() -> CRUDCafe:
    """Возвращает CRUD для модели Cafes."""
    return CRUDCafe(Cafes)


def get_slot_crud() -> CRUDSlot:
    """Возвращает CRUD для модели Slots."""
    return CRUDSlot(Slots)
