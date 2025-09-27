from fastapi import status

from src.exceptions.auth import BaseAPIException


class SlotNotFoundException(BaseAPIException):
    """Исключение 404: слот не найден."""

    error_code: str = "SlotNotFound"

    def __init__(self, detail: str = "Слот не найден") -> None:
        """Создать исключение 404 для отсутствующего слота."""
        super().__init__(detail, status.HTTP_404_NOT_FOUND)


class CafeOrSlotNotFoundException(BaseAPIException):
    """Исключение 404: кафе или слот не найдены."""

    error_code: str = "CafeOrSlotNotFound"

    def __init__(self, detail: str = "Кафе или слот не найдены") -> None:
        """Создать исключение 404 для отсутствующего кафе или слота."""
        super().__init__(detail, status.HTTP_404_NOT_FOUND)


class SlotOverlapException(BaseAPIException):
    """Исключение 400: пересечение интервала активного слота."""

    error_code: str = "SlotOverlap"

    def __init__(
        self,
        detail: str = (
            "Интервал времени слота пересекается "
            "с существующим активным слотом"
        ),
    ) -> None:
        """Создать исключение 400 для пересечения временных интервалов."""
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)


class CafeIdMismatchException(BaseAPIException):
    """Исключение 400: cafe_id в теле и пути не совпадают."""

    error_code: str = "CafeIdMismatch"

    def __init__(
        self,
        detail: str = "cafe_id в теле и в пути должны совпадать",
    ) -> None:
        """Создать исключение 400 при несовпадении cafe_id."""
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)


class CafeIdChangeForbiddenException(BaseAPIException):
    """Исключение 400: изменение cafe_id запрещено."""

    error_code: str = "CafeIdChangeForbidden"

    def __init__(
        self,
        detail: str = "Менять cafe_id у существующего слота запрещено",
    ) -> None:
        """Создать исключение 400 при попытке сменить cafe_id."""
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)
