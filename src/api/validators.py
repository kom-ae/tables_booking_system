from typing import Any, Callable, List, Optional, Union

from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.responses.cafes import cafe_check_duplicate_responses
from src.core.logger import logger
from src.crud.action import actions_crud
from src.crud.factory import get_cafe_crud
from src.models import Action, User
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
        logger.warning(
            f'Попытка создать дубликат кафе: {cafe.name}, {cafe.address}',
            user=None,
        )
        raise HTTPException(**cafe_check_duplicate_responses)


async def check_action_exist(
    action_id: int,
    session: AsyncSession,
) -> Action:
    """Проверяет на наличие доступа и акции."""
    action = await actions_crud.get(
        obj_id=action_id,
        session=session,
    )
    if action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Акция не найдена',
        )
    return action


async def handler_run_crud_cafe(
    func: Callable[..., Any],
    **kwargs: Any,
) -> Union[CafeDB, List[CafeDB]]:
    """Запуск корутины CRUD и логирование результата через logger."""
    crud_args: dict = kwargs.get('crud_args', {})
    msg_log: str = kwargs.get('msg_log', '')
    user: Optional[User] = kwargs.get('user', None)

    try:
        obj = await func(**crud_args)

        if obj is not None:
            msg_log_full = msg_log
            if hasattr(obj, 'id'):
                msg_log_full += str(obj.id)
            msg_log_full += '. Успешно.'
            logger.info(msg_log_full, user=user)

        return obj

    except RequestValidationError as err:
        logger.error(
            f'Ошибка валидации при выполнении {func.__name__}: {err.body}',
            user=user,
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Ошибка валидации данных.',
        )

    except Exception as err:
        logger.error(
            f'Ошибка при выполнении {func.__name__} '
            f'в модуле {func.__module__}: {str(err)}',
            user=user,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Внутренняя ошибка сервера.',
        )
