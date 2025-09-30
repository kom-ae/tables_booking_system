from fastapi import status
from fastapi.responses import JSONResponse

from src.exceptions.base import AppException


# === Ошибки базы данных ===
class DBException(AppException):
    """Ошибка БД."""

    error_code: str = 'DBError'

    def __init__(
        self,
        message: str = 'Ошибка базы данных',
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> None:
        """Исключение БД."""
        super().__init__(message, status_code)


class DBIntegrityException(DBException):
    """Ошибка целостности."""

    error_code: str = 'DBIntegrityError'

    def __init__(self, message: str = 'Ошибка целостности данных') -> None:
        """Исключение 400."""
        super().__init__(message, status.HTTP_400_BAD_REQUEST)

    def to_response(self) -> JSONResponse:
        """JSON-ответ."""
        msg: str = self.message
        if 'UNIQUE constraint failed' in msg:
            field: str = msg.split(':')[-1].strip().split('.')[-1]
            msg = f'Пользователь с таким {field} уже существует'
        return JSONResponse(
            status_code=self.status_code,
            content={'error': self.error_code, 'message': msg},
        )
