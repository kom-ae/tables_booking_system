from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logger import log_event
from src.crud.base import CRUDBase
from src.models import Cafes, User
from src.schemas.cafes import CafeCreate, CafeDB


class CRUDCafe(CRUDBase):
    """CRUD для кафе."""

    async def create_cafe(
        self,
        obj_in: CafeCreate,
        session: AsyncSession,
        user: Optional[User] = None,
    ) -> CafeDB:
        """Создание кафе."""
        in_managers = obj_in.model_dump(include='managers').get('managers', [])
        obj_in_data = obj_in.model_dump(exclude='managers')

        db_obj_managers = (await session.scalars(
            select(User).where(User.id.in_(in_managers)),
        )).all()

        db_obj = Cafes(**obj_in_data)
        db_obj.managers = db_obj_managers
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        log_event(
            'info',
            f'Создано кафе, id={db_obj.id} '
            f'с данными: {obj_in_data}',
            **{'username': user.username, 'user_id': user.id} if user else {},
        )
        return db_obj

    async def get_by_name_address(
            self,
            name: str,
            address: str,
            session: AsyncSession,
    ) -> Optional[Cafes]:
        """Поиск кафе по имени и адресу."""
        return (await session.scalars(select(Cafes).where(
                and_(
                    Cafes.name == name,
                    Cafes.address == address,
                )))
                ).first()
