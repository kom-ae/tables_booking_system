from fastapi import status

from src.exceptions.auth import BaseAPIException


class SlotNotFoundException(BaseAPIException):
    """Исключение 404: слот не найден."""
    error_code: str = 'SlotNotFound'

    def __init__(self, detail: str = 'Слот не найден') -> None:
        super().__init__(detail, status.HTTP_404_NOT_FOUND)


class CafeOrSlotNotFoundException(BaseAPIException):
    """Исключение 404: кафе или слот не найдены."""
    error_code: str = 'CafeOrSlotNotFound'

    def __init__(self, detail: str = 'Кафе или слот не найдены') -> None:
        super().__init__(detail, status.HTTP_404_NOT_FOUND)


class SlotOverlapException(BaseAPIException):
    """Исключение 400: интервал времени слота пересекается с существующим активным слотом."""
    error_code: str = 'SlotOverlap'

    def __init__(
        self,
        detail: str = (
            'Интервал времени слота пересекается с существующим активным слотом'
        ),
    ) -> None:
        super().__init__(detail, status.HTTP_400_BAD_REQUEST)
