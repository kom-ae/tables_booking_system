from fastapi import status

from src.exceptions.base import AppException


class InvalidNameCafeException(AppException):
    """Некорректное имя кафе."""

    error_code: str = 'InvalidNameCafe'

    def __init__(
        self,
        detail: str = 'Имя кафе не может быть из одних спецсимволов.',
    ) -> None:
        """Исключение 400."""
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)


class InvalidFieldsCafeException(AppException):
    """Некорректные значения полей кафе."""

    error_code: str = 'InvalidFieldsCafe'

    def __init__(self, detail: str = 'Поля кафе не могут быть null.') -> None:
        """Исключение 400."""
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)
