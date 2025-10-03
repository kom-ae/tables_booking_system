from src.crud.cafes import CRUDCafe
from src.crud.dishes import CRUDDish
from src.crud.tables import CRUDTable
from src.crud.users import CRUDUser
from src.models import Cafe, Dishe, Table, User  # noqa


def get_user_crud() -> CRUDUser:
    """Возвращает CRUD для модели User."""
    return CRUDUser(User)


def get_cafe_crud() -> CRUDCafe:
    """Возвращает CRUD для модели Cafe."""
    return CRUDCafe(Cafe)


def get_table_crud() -> CRUDTable:
    """Возвращает CRUD для модели Tables."""
    return CRUDTable(Table)


def get_dish_crud() -> CRUDDish:
    """Возвращает CRUD для модели Dishe."""
    return CRUDDish(Dishe)
