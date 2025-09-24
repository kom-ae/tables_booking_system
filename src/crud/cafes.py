from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logger import log_event
from src.crud.base import CRUDBase
from src.models import Cafes, User
from src.schemas.cafes import CafeCreate, CafeUpdate


class CRUDCafe(CRUDBase[Cafes, CafeCreate, CafeUpdate]):
    """CRUD для кафе."""

    async def create_cafe(
        self,
        obj_in: CafeCreate,
        session: AsyncSession,
        user: Optional[User] = None,
    ) -> Cafes:
        """Создание кафе."""
        in_managers = obj_in.model_dump(include='managers').get('managers')
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

    def encoder(obj):
        if isinstance(obj, list[User]):
            return []
        return obj

    async def update(
            self,
            db_obj: Cafes,
            obj_in: CafeUpdate,
            session: AsyncSession
    ) -> Cafes:
        """Обновление кафе."""
        obj_data = jsonable_encoder(db_obj, exclude={'managers'})
        update_data = obj_in.model_dump(exclude_unset=True, exclude='managers')
        in_managers = obj_in.model_dump(include='managers').get('managers')

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db_obj_managers = (await session.scalars(
            select(User).where(User.id.in_(in_managers)),
        )).all()

        db_obj.managers = db_obj_managers

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
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
