from pydantic import BaseModel


class Auth(BaseModel):
    """Схема для передачи данных аутентификации пользователя."""

    name: str
    password: str


class TokenResponse(BaseModel):
    """Схема ответа с JWT-токеном после успешной аутентификации."""

    token: str
