from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.exceptions.auth import InvalidCredentialsException
from src.api.responses.auth import login_responses, logout_responses
from src.api.utils.auth import create_access_token, verify_password
from src.core.db import get_async_session
from src.core.user import get_user_by_name
from src.schemas.auth import Auth, TokenResponse

router = APIRouter()


@router.post(
    '/login',
    response_model=TokenResponse,
    responses=login_responses,
    status_code=status.HTTP_200_OK,
    summary='Аутентификация пользователя',
)
async def login(
    auth: Auth,
    db: AsyncSession = Depends(get_async_session),
) -> TokenResponse:
    """Авторизация пользователя и выдача JWT по email или телефону."""
    user = await get_user_by_name(auth.name, db)
    if not user or not verify_password(auth.password, user.password):
        raise InvalidCredentialsException()
    token = create_access_token(data={'sub': str(user.id)})
    return {'token': token}


@router.post(
    '/logout',
    responses=logout_responses,
    summary='Выход из аккаунта',
)
async def logout() -> None:
    """Выход пользователя (информативно, JWT статический)."""
    return {'message': 'Вы вышли из системы.'}
