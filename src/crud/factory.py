from src.crud.cafes import CRUDCafe
from src.crud.user import CRUDUser
from src.models import Cafes, User


def get_user_crud() -> CRUDUser:
    """Возвращает CRUD для модели User."""
    return CRUDUser(User)


def get_cafe_crud() -> CRUDCafe:
    """Возвращает CRUD для модели Cafes."""
    return CRUDCafe(Cafes)
