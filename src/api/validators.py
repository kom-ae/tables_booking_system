from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.factory import get_cafe_crud
from src.schemas.cafes import CafeCreate


cafe_crud = get_cafe_crud()


async def check_duplicate_cafe(
    cafe: CafeCreate,
    session: AsyncSession,
) -> None:
    """Проверить на существование дубликата кафе."""
    db_obj = await cafe_crud.get_by_name_address(
        name=cafe.name,
        address=cafe.address,
        session=session,
    )
    if db_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Кафе с таким именем и адресом уже существует.',
        )
