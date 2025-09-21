from src.crud.user import CRUDUser
from src.models.user import User


def get_user_crud() -> CRUDUser:
    """Возвращает CRUD для модели User."""
    return CRUDUser(User)
