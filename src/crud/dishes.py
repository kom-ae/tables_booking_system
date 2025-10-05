from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.base import CRUDBase
from src.models.dish import Dishe
from src.schemas.dish import DishCreate, DishUpdate


class CRUDDish(CRUDBase[Dishe, DishCreate, DishUpdate]):
    """CRUD для блюд."""

    async def get_by_id_and_cafe(
        self,
        dish_id: Optional[int] = None,
        cafe_id: Optional[int] = None,
        session: AsyncSession = None,
        only_active: bool = True,
    ) -> Optional[Dishe] | List[Dishe]:
        """Получить блюдо по cafe_id и dish_id."""
        query = select(self.model)
        conditions = []

        if dish_id is not None:
            conditions.append(self.model.id == dish_id)
        if cafe_id is not None:
            conditions.append(self.model.cafe_id == cafe_id)
        if conditions:
            query = query.where(and_(*conditions))
        if only_active:
            query = query.where(self.model.is_active)

        result = await session.scalars(query)
        if dish_id is not None:
            return result.first()
        return result.all()

    async def get_dishes_by_cafe_id(
        self,
        cafe_id: int,
        session: AsyncSession,
        only_active: bool = True,
    ) -> List[Dishe]:
        """Список блюд по ID кафе."""
        result = await self.get_by_id_and_cafe(
            dish_id=None,
            cafe_id=cafe_id,
            session=session,
            only_active=only_active,
        )
        return result if isinstance(result, list) else []

    async def get_all_dishes(
        self,
        session: AsyncSession,
        only_active: bool = True,
    ) -> List[Dishe]:
        """Получить все блюда."""
        if only_active:
            return await self.get_multi_active(session)
        return await self.get_multi_all(session)

    async def create_dish(
        self,
        obj_in: DishCreate,
        session: AsyncSession,
    ) -> Dishe:
        """Создать блюдо в кафе."""
        obj_data = obj_in.model_dump()
        obj_data["cafe_id"] = obj_data.pop("cafe")
        db_obj = Dishe(**obj_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update_dish(
        self,
        dish_obj: Dishe,
        obj_in: DishUpdate,
        session: AsyncSession,
    ) -> Dishe:
        """Обновить блюдо."""
        obj_data = obj_in.model_dump(exclude_unset=True)
        if "cafe" in obj_data.keys():
            obj_data["cafe_id"] = obj_data.pop("cafe")
        for field, value in obj_data.items():
            setattr(dish_obj, field, value)
        session.add(dish_obj)
        await session.commit()
        await session.refresh(dish_obj)
        return dish_obj

    async def get_dish_by_name_and_cafe(
        self,
        name: str,
        cafe_id: int,
        session: AsyncSession,
    ) -> Optional[Dishe]:
        """Поиск блюда по названию и кафе."""
        return (
            await session.scalars(
                select(Dishe).where(
                    and_(
                        Dishe.name == name,
                        Dishe.cafe_id == cafe_id,
                    ),
                ),
            )
        ).first()

    async def get_dishes_by_price_range(
        self,
        cafe_id: int,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        session: AsyncSession = None,
        only_active: bool = True,
    ) -> List[Dishe]:
        """Получить блюда по диапазону цен."""
        query = select(self.model).where(self.model.cafe_id == cafe_id)

        if min_price is not None:
            query = query.where(self.model.price >= min_price)
        if max_price is not None:
            query = query.where(self.model.price <= max_price)
        if only_active:
            query = query.where(self.model.is_active)

        result = await session.scalars(query)
        return result.all()


dish = CRUDDish(Dishe)
