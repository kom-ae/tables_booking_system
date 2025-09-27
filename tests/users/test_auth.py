import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.schemas.auth import Auth
from src.schemas.users import UserCreate
from tests.users.conftest import (
    EMAIL_ONE,
    EMAIL_TWO,
    PHONE_ONE,
    PHONE_TWO,
    USERNAME_ONE,
    USERNAME_TWO,
    VALID_PASSWORD,
    user_crud,
)


@pytest.mark.asyncio
async def test_login_by_email(
    client_fixture: AsyncClient,
    session_fixture: AsyncSession,
) -> None:
    """Тест авторизации пользователя по email."""
    user_in: UserCreate = UserCreate(
        username=USERNAME_ONE,
        email=EMAIL_ONE,
        password=VALID_PASSWORD,
        phone=PHONE_ONE,
    )
    await user_crud.create(obj_in=user_in, session=session_fixture)

    payload: dict = Auth(
        name=EMAIL_ONE,
        password=VALID_PASSWORD,
    ).model_dump()
    response = await client_fixture.post('/auth/login', json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert 'token' in response.json()


@pytest.mark.asyncio
async def test_login_by_phone(
    client_fixture: AsyncClient,
    session_fixture: AsyncSession,
) -> None:
    """Тест авторизации пользователя по телефону."""
    user_in: UserCreate = UserCreate(
        username=USERNAME_TWO,
        email=EMAIL_TWO,
        password=VALID_PASSWORD,
        phone=PHONE_TWO,
    )
    await user_crud.create(obj_in=user_in, session=session_fixture)

    payload: dict = Auth(
        name=PHONE_TWO,
        password=VALID_PASSWORD,
    ).model_dump()
    response = await client_fixture.post('/auth/login', json=payload)
    assert response.status_code == status.HTTP_200_OK
    assert 'token' in response.json()
