from typing import Any, List, Optional, Union

from fastapi import Depends, HTTPException, Path, status
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.responses.cafes import cafe_check_duplicate_responses
from src.core.db import get_async_session
from src.core.logger import log_event
from src.crud.factory import get_cafe_crud, get_slot_crud
from src.models.cafes import Cafes
from src.models.slots import Slots
from src.models.user import User
from src.schemas.cafes import CafeCreate, CafeDB

cafe_crud = get_cafe_crud()
slot_crud = get_slot_crud()


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
        raise HTTPException(**cafe_check_duplicate_responses)


async def handler_run_crud_cafe(
    func: callable,
    **kwargs: Any,
) -> Union[CafeDB, List[CafeDB]]:
    """Запуск корутины и логирование результатов."""
    crud_args: dict = kwargs.get('crud_args', {})
    msg_log: str = kwargs.get('msg_log', '')
    user: Optional[User] = kwargs.get('user', None)
    user_log: dict = (
        {'username': user.username, 'user_id': user.id} if user else {}
    )
    try:
        if obj := await func(**crud_args):
            msg_log_full = (
                msg_log
                + (str(obj.id) if not isinstance(obj, list) else '')
                + '. Успешно.'
            )
            log_event('info', msg_log_full, **user_log)
    except RequestValidationError as err:
        log_event(
            'error',
            f'При выполнении функции {func.__name__}. '
            f'Ошибка валидации данных: {err.body}',
            **user_log,
        )
        raise
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


async def cafe_exists(
    cafe_id: int = Path(..., ge=1, description='ID кафе'),
    session: AsyncSession = Depends(get_async_session),
) -> Cafes:
    """Возвращает кафе по ID или 404."""
    cafe = await cafe_crud.get(obj_id=cafe_id, session=session)
    if not cafe:
        raise HTTPException(status_code=404, detail='Кафе не найдено')
    return cafe


async def require_admin_or_manager(
    user: User = Depends(),
) -> User:
    """Разрешить только superuser/admin/manager."""
    role = getattr(user, 'role', None)
    is_superuser = bool(getattr(user, 'is_superuser', False))
    if is_superuser or role in {'admin', 'manager'}:
        return user
    raise HTTPException(status_code=403, detail='Недостаточно прав')


async def slot_in_cafe_exists(
    cafe_id: int = Path(..., ge=1, description='ID кафе'),
    time_slot_id: int = Path(..., ge=1, description='ID слота'),
    session: AsyncSession = Depends(get_async_session),
) -> Slots:
    """Слот существует и относится к указанному кафе, иначе 404."""
    slot = await slot_crud.get(obj_id=time_slot_id, session=session)
    if not slot or slot.cafe_id != cafe_id:
        raise HTTPException(status_code=404, detail='Слот не найден')
    return slot


async def visible_slot_for_user(
    cafe_id: int = Path(..., ge=1, description='ID кафе'),
    time_slot_id: int = Path(..., ge=1, description='ID слота'),
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(),
) -> Slots:
    """
    Возвращает слот для просмотра:
    - admin/manager/superuser видят любой слот;
    - обычные пользователи видят только активный,
      иначе получат 404 (чтобы не палить наличие неактивного).
    """
    slot = await slot_in_cafe_exists(cafe_id, time_slot_id, session)
    role = getattr(user, 'role', None)
    is_superuser = bool(getattr(user, 'is_superuser', False))
    if is_superuser or role in {'admin', 'manager'}:
        return slot
    if not slot.is_active:
        raise HTTPException(status_code=404, detail='Слот не найден')
    return slot
