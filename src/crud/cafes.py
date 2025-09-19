from src.crud.base import CRUDBase
from src.models import Cafes


class CRUDCafe(CRUDBase):
    pass


cafes_crud = CRUDCafe(Cafes)
