from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.action import actions_crud
from src.models import Actions


async def check_action_exist(
        action_id: int,
        session: AsyncSession,
) -> Actions:
    """Проверяет на наличие доступа и акции."""
    action = await actions_crud.get(
        obj_id=action_id, session=session,
    )
    if action is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Акция не найдена',
        )
    return action
