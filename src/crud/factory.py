from src.crud.cafes import CRUDCafe
from src.crud.tables import CRUDTable
from src.crud.users import CRUDUser
from src.models import Cafe, Dishe, Tables, User  # noqa


def get_user_crud() -> CRUDUser:
    """Возвращает CRUD для модели User."""
    return CRUDUser(User)


def get_cafe_crud() -> CRUDCafe:
    """Возвращает CRUD для модели Cafe."""
    return CRUDCafe(Cafe)


def get_table_crud() -> CRUDTable:
    """Возвращает CRUD для модели Tables."""
    return CRUDTable(Tables)

# def get_dishe_crud() -> CRUDDishe:
#    """Возвращает CRUD для модели Dishe."""
#    return CRUDUser(Dishe)
