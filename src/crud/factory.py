from src.crud.cafes import CRUDCafe
from src.crud.users import CRUDUser

# from src.crud.dish import CRUDDish
from src.models import Cafe, Dishe, User  # noqa


def get_user_crud() -> CRUDUser:
    """Возвращает CRUD для модели User."""
    return CRUDUser(User)


def get_cafe_crud() -> CRUDCafe:
    """Возвращает CRUD для модели Cafe."""
    return CRUDUser(User)


# def get_dishe_crud() -> CRUDDishe:
#    """Возвращает CRUD для модели Dishe."""
#    return CRUDUser(User)
