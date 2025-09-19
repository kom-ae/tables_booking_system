from typing import Optional

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_async_session
from src.core.user import current_user, current_superuser, current_manager

from src.schemas.action import Actions, ActionsCreate, ActionsUpdate
from src.crud.action import actions_crud
from src.models import User


router = APIRouter()


@router.get(
    '',
    response_model=list[Actions],
    response_model_exclude=True,
    summary=('Получение списка акций(только для администратора и менеджера, пользователь - только активные)')
)
async def get_actions(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_user),
    auth_check: User = Depends(current_manager),
    cafe_id: Optional[int] = Query(
        None,
        description='Показать акции только в указанном кафе'
    ),
    show_all: bool = Query(
        False,
        description='Показать все акции (только для админа/менеджера)'
    )
):
    """Получение списка акций (только для администратора и менеджера, пользователь - только активные)"""
    actions = await actions_crud.get_all_actions(
        session=session,
        cafe_id=cafe_id,
        show_all=show_all,
        current_user=current_user
    )
    return actions


@router.post(
    '',
    response_model=Actions,
    response_model_exclude=True,
    dependencies=[Depends(current_superuser)]
)
async def create_action(
    action: ActionsCreate,
    session: AsyncSession = Depends(get_async_session)
):
    new_action = await actions_crud.create(
        obj_in=action, session=session
    )
    return new_action


@router.get(
    '/{action_id}',
    response_model=Actions,
    response_model_exclude=True
)
async def get_action_by_id(
    action_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    action = await actions_crud.get(action_id, session)
    return action


@router.patch(
    '/{action_id}',
    response_model=Actions,
    response_model_exclude=True,
    dependencies=[Depends(current_superuser)]
)
async def update_action_by_id(
    action_id: int,
    update_data: ActionsUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    pass