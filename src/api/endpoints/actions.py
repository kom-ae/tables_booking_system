from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.responses.actions import (
    action_create_responses,
    action_get_responses,
    action_not_found,
    action_update_responses,
    actions_list_responses,
)
from src.api.validators import check_action_exist
from src.core.db import get_async_session
from src.core.logger import log_endpoint, log_event
from src.core.user import current_admin, current_manager, current_user
from src.crud.action import actions_crud
from src.models import User
from src.schemas.action import ActionsCreate, ActionsDB, ActionsUpdate

router = APIRouter()


@router.get(
    '',
    response_model=list[ActionsDB],
    response_model_exclude_none=True,
    response_description='Список акций',
    responses=actions_list_responses,
    summary='Получение списка акций'
    ' (только для администратора, пользователь - только активные).',
)
@log_endpoint()
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
    actions = await actions_crud.get_all_actions(
        session=session,
        current_user=current_user,
        cafe_id=cafe_id,
        show_all=show_all,
    )

    log_event(
        'info',
        f'Получен список акций, show_all={show_all}',
        username=current_user.username,
        user_id=current_user.id,
    )

    return actions


@router.post(
    '',
    response_model=ActionsDB,
    response_model_exclude_none=True,
    response_description='Данные созданной акции',
    responses=action_create_responses,
    dependencies=[Depends(current_manager)],
    summary='Создание акций'
    ' (только для администратора и менеджера).',
)
@log_endpoint()
async def create_action(
    action: ActionsCreate,
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(current_admin),
) -> ActionsDB:
    """Создание акций."""
    new_action = await actions_crud.create_action(
        obj_in=action, session=session,
    )

    log_event(
        'info',
        f'Создана новая акция с ID {new_action.id}',
        username=admin.username,
        user_id=admin.id,
    )

    return new_action


@router.get(
    '/{action_id}',
    response_model=ActionsDB,
    response_model_exclude_none=True,
    responses=action_get_responses,
    summary='Получение акции по ID'
    ' (только для администратора и менеджера, пользователь - только активные)',
    dependencies=[Depends(current_user)],
)
@log_endpoint()
async def get_action_by_id(
    action_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(current_user),
) -> ActionsDB:
    """Получение акции по ID."""
    action = await actions_crud.get_action(
        session,
        action_id,
        current_user,
    )

    if action is None:
        raise HTTPException(**action_not_found)

    log_event(
        'info',
        f'Получена акция. ID {action_id}.',
        username=current_user.username,
        user_id=current_user.id,
    )

    return action


@router.patch(
    '/{action_id}',
    response_model=ActionsDB,
    response_model_exclude_none=True,
    responses=action_update_responses,
    summary='Обновление акции по ID (только для администратора и менеджера)',
    dependencies=[Depends(current_manager)],
)
@log_endpoint()
async def update_action_by_id(
    action_id: int,
    update_data: ActionsUpdate,
    session: AsyncSession = Depends(get_async_session),
    admin: User = Depends(current_admin),
) -> ActionsDB:
    """Обновление акции по ID."""
    action = await check_action_exist(
        action_id=action_id,
        session=session,
    )

    action = await actions_crud.update_action(
        db_obj=action,
        obj_in=update_data,
        session=session,
    )

    log_event(
        'info',
        f'Обновлены данные по акции с ID {action_id}',
        username=admin.username,
        user_id=admin.id,
    )

    return action
