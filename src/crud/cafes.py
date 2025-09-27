from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models import Cafe, User
from src.schemas.cafes import CafeCreate, CafeDB


class CRUDCafe(CRUDBase):
    """CRUD для кафе."""

    async def create_cafe(
        self,
        obj_in: CafeCreate,
        session: AsyncSession,
    ) -> CafeDB:
        """Создание кафе."""
        in_managers = obj_in.model_dump(include={'managers'}).get(
            'managers',
            [],
        )
        obj_in_data = obj_in.model_dump(exclude={'managers'})
        obj_in_data['updated_at'] = func.now()

        db_obj_managers = await session.scalars(
            select(User).where(User.id.in_(in_managers)),
        )
        db_obj_managers = db_obj_managers.all()

        db_obj = Cafe(**obj_in_data)
        db_obj.managers = db_obj_managers

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)

        return CafeDB.model_validate(db_obj, from_attributes=True)
