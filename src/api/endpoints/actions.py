from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.validators import check_action_exist
from src.core.db import get_async_session
from src.core.user import current_manager, current_user
from src.crud.action import actions_crud
from src.models import User
from src.schemas.action import ActionsCreate, ActionsDB, ActionsUpdate

router = APIRouter()


@router.get(
    '',
    response_model=list[ActionsDB],
    response_model_exclude_none=True,
    summary='Получение списка акций'
    ' (только для администратора, пользователь - только активные).',
)
async def get_actions(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_user),
    cafe_id: Optional[int] = Query(
        None,
        description='Показать акции только в указанном кафе',
    ),
    show_all: bool = Query(
        False,
        description='Показать все акции (только для админа/менеджера)',
    ),
) -> list[ActionsDB]:
    """Получение списка акций."""
    if current_user.is_admin() and show_all:
        return await actions_crud.get_all_actions(
            session=session,
            cafe_id=cafe_id,
            show_all=show_all,
        )
    return await actions_crud.get_all_active_actions(session, cafe_id)


@router.post(
    '',
    response_model=ActionsDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_manager)],
    summary='Создание акций'
    ' (только для администратора и менеджера).',
)
async def create_action(
    action: ActionsCreate,
    session: AsyncSession = Depends(get_async_session),
) -> ActionsDB:
    """Создание акций."""
    return await actions_crud.create_action(
        obj_in=action, session=session,
    )


@router.get(
    '/{action_id}',
    response_model=ActionsDB,
    response_model_exclude_none=True,
    summary='Получение акции по ID'
    ' (только для администратора и менеджера, пользователь - только активные)',
    dependencies=[Depends(current_user)],
)
async def get_action_by_id(
    action_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_user),
) -> ActionsDB:
    """Получение акции по ID."""
    await check_action_exist(
        action_id=action_id,
        session=session,
    )
    if current_user.is_admin():
        return await actions_crud.get_action(
            session=session,
            action_id=action_id,
        )
    action = await actions_crud.get_acive_action(
        session=session,
        action_id=action_id,
    )
    if action is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Акция не найдена',
        )
    return action


@router.patch(
    '/{action_id}',
    response_model=ActionsDB,
    response_model_exclude_none=True,
    summary='Обновление акции по ID (только для администратора и менеджера)',
    dependencies=[Depends(current_manager)],
)
async def update_action_by_id(
    action_id: int,
    update_data: ActionsUpdate,
    session: AsyncSession = Depends(get_async_session),
) -> ActionsDB:
    """Обновление акции по ID."""
    action = await check_action_exist(
        action_id=action_id,
        session=session,
    )

    return await actions_crud.update_action(
        db_obj=action,
        obj_in=update_data,
        session=session,
    )
