from typing import Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logger import project_log
from src.crud.base import CRUDBase
from src.models import Cafe, User
from src.schemas.cafes import CafeCreate, CafeDB, CafeUpdate


class CRUDCafe(CRUDBase[Cafe, CafeCreate, CafeUpdate]):
    """CRUD для модели Cafe с логированием."""

    async def create_cafe(
        self,
        obj_in: CafeCreate,
        session: AsyncSession,
        user: Optional[User] = None,
    ) -> CafeDB:
        """Создание кафе с менеджерами."""
        in_managers: list[int] = obj_in.model_dump(include={'managers'}).get(
            'managers',
            [],
        )
        obj_in_data = obj_in.model_dump(exclude={'managers'})
        db_obj_managers = await session.scalars(
            select(User).where(User.id.in_(in_managers)),
        )
        db_obj_managers = db_obj_managers.all()
        db_obj = Cafe(**obj_in_data)
        db_obj.managers = db_obj_managers

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)

        project_log(
            'info',
            f'Создано кафе {db_obj.name} с id={db_obj.id}',
            user=user,
        )
        return CafeDB.model_validate(db_obj, from_attributes=True)

    async def update(
        self,
        db_obj: Cafe,
        obj_in: CafeUpdate,
        session: AsyncSession,
        user: Optional[User] = None,
    ) -> Cafe:
        """Обновление данных кафе и менеджеров через PATCH."""
        update_data = obj_in.model_dump(
            exclude_unset=True,
            exclude={'managers'},
        )
        in_managers: list[int] = obj_in.model_dump(include={'managers'}).get(
            'managers',
            [],
        )

        for field, value in update_data.items():
            if value is not None:
                setattr(db_obj, field, value)

        if in_managers:
            db_obj_managers = await session.scalars(
                select(User).where(User.id.in_(in_managers)),
            )
            db_obj.managers = db_obj_managers.all()

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)

        project_log(
            'info',
            f'Обновлено кафе {db_obj.name} с id={db_obj.id}',
            user=user,
        )
        return db_obj

    async def get_by_name_address(
        self,
        name: str,
        address: str,
        session: AsyncSession,
    ) -> Optional[Cafe]:
        """Получение кафе по имени и адресу."""
        result = await session.scalars(
            select(Cafe).where(
                and_(Cafe.name == name, Cafe.address == address),
            ),
        )
        cafe = result.first()
        if cafe:
            project_log('info', f'Найдено кафе {name} по адресу {address}')
        return cafe
