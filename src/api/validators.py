from typing import Any, List, Optional, Union

from fastapi import status
from fastapi.exceptions import HTTPException, RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.responses.cafes import cafe_check_duplicate_responses
from src.core.logger import log_event
from src.crud.action import actions_crud
from src.crud.factory import get_cafe_crud
from src.models import Actions, User
from src.schemas.cafes import CafeCreate, CafeDB

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
            **cafe_check_duplicate_responses,
        )


async def handler_run_crud_cafe(func: callable, **kwargs: Any) -> Union[
        CafeDB, List[CafeDB],
]:
    """Запуск корутины и логирование результатов."""
    crud_args: dict = kwargs.get('crud_args', {})
    msg_log: str = kwargs.get('msg_log', '')
    user: Optional[User] = kwargs.get('user', None)
    user_log: dict = {'username': user.username, 'user_id': user.id,
                      } if user else {}
    try:
        if obj := await func(**crud_args):
            msg_log_full = (
                msg_log + (str(obj.id) if not isinstance(obj, list) else '') +
                '. Успешно.'
            )
            log_event('info', msg_log_full, **user_log)
    except RequestValidationError as err:
        log_event(
            'error',
            f'При выполнении функции {func.__name__}. '
            f'Ошибка валидации данных: {err.body}',
            **user_log,
        )
    except Exception as err:
        log_event(
            'error',
            f'При выполнении функции {func.__name__} в модуле '
            f'{func.__module__}. Произошла ошибка: {str(err)}',
            **user_log,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Ошибка сервера.',
        )
    return obj


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
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Акция не найдена',
        )
    return action
