from src.crud.cafes import CRUDCafe
from src.crud.users import CRUDUser
from src.crud.tables import CRUDTable
from src.models import Cafes, User, Tables


def get_user_crud() -> CRUDUser:
    """Возвращает CRUD для модели User."""
    return CRUDUser(User)


def get_cafe_crud() -> CRUDCafe:
    """Возвращает CRUD для модели Cafes."""
    return CRUDCafe(Cafes)


def get_table_crud() -> CRUDTable:
    """Возвращает CRUD для модели Tables."""
    return CRUDTable(Tables)
