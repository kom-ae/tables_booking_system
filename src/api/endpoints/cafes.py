from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.core.user import current_superuser, current_user
from src.crud.cafes import cafes_crud
from src.schemas.cafes import CafeDB

router = APIRouter()


@router.get(
    '/',
    response_model=list[CafeDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_user), Depends(current_superuser)]
)
async def get_all_cafes(
    session: AsyncSession = Depends(get_async_session)
):
    """Получение списка кафе

    (только для администратора, пользователь - только активные)."""

    return await cafes_crud.get_multi(session)
