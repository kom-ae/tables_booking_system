from fastapi import status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Базовое исключение."""

    error_code: str = 'AppError'

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> None:
        """Исключение."""
        self.message = message
        self.status_code = int(status_code)
        super().__init__(message)

    def to_response(self) -> JSONResponse:
        """JSON-ответ."""
        return JSONResponse(
            status_code=self.status_code,
            content={'error': self.error_code, 'message': self.message},
        )
