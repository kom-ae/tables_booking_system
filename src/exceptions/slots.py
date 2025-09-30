from fastapi import status

from src.exceptions.base import AppException


class SlotNotFoundException(AppException):
    """Исключение 404: слот не найден."""
    error_code: str = 'SlotNotFound'

    def __init__(self, detail: str = 'Слот не найден') -> None:
        super().__init__(detail, status.HTTP_404_NOT_FOUND)


class CafeOrSlotNotFoundException(AppException):
    """Исключение 404: кафе или слот не найдены."""
    error_code: str = 'CafeOrSlotNotFound'

    def __init__(self, detail: str = 'Кафе или слот не найдены') -> None:
        super().__init__(detail, status.HTTP_404_NOT_FOUND)


class SlotOverlapException(AppException):
    """Исключение 400: пересечение интервала активного слота."""
    error_code: str = 'SlotOverlap'

    def __init__(self) -> None:
        detail = (
            'Интервал времени слота пересекается с существующим '
            'активным слотом'
        )
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)


class CafeIdMismatchException(AppException):
    """Исключение 400: cafe_id в теле и пути не совпадают."""
    error_code: str = 'CafeIdMismatch'

    def __init__(self) -> None:
        detail = 'cafe_id в теле и в пути должны совпадать'
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)


class CafeIdChangeForbiddenException(AppException):
    """Исключение 400: изменение cafe_id запрещено."""
    error_code: str = 'CafeIdChangeForbidden'

    def __init__(self) -> None:
        detail = 'Менять cafe_id у существующего слота запрещено'
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)
