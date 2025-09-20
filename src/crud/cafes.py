from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models import Cafes, User
from src.schemas.cafes import CafeCreate, CafeDB


class CRUDCafe(CRUDBase):
    """CRUD для кафе."""

    async def create_cafe(
        self,
        obj_in: CafeCreate,
        session: AsyncSession,
    ) -> CafeDB:
        """Корутина для создания кафе."""
        obj_in_data = obj_in.model_dump(exclude='managers')
        obj_in_data['updated_at'] = func.now()
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def create_cafe_manager(
        self,
        cafe: Cafes,
        managers: list[dict],
        session: AsyncSession,
    ) -> None:
        """Корутина для создания менеджеров кафе."""
        for manager in managers:
            db_manager = await session.execute(
                select(User).where(User.id == manager['id']),
            )
            db_manager = db_manager.scalar_one()
            cafe.users.append(db_manager)
        await session.commit()


cafes_crud = CRUDCafe(Cafes)
