from fastapi import status

from src.api.responses.constants import BOOKING_RESPONSES
from src.schemas.bookings import Booking


booking_list_responses = {
    status.HTTP_200_OK: {
        'description': 'Список бронирований',
        'model': list[Booking],
    },
    status.HTTP_401_UNAUTHORIZED: BOOKING_RESPONSES[
        status.HTTP_401_UNAUTHORIZED
    ],
}

booking_get_responses = {
    status.HTTP_200_OK: BOOKING_RESPONSES[status.HTTP_200_OK],
    status.HTTP_401_UNAUTHORIZED: BOOKING_RESPONSES[
        status.HTTP_401_UNAUTHORIZED
    ],
    status.HTTP_404_NOT_FOUND: BOOKING_RESPONSES[
        status.HTTP_404_NOT_FOUND
    ],
}

booking_create_responses = {
    status.HTTP_201_CREATED: BOOKING_RESPONSES[status.HTTP_201_CREATED],
    status.HTTP_400_BAD_REQUEST: BOOKING_RESPONSES[
        status.HTTP_400_BAD_REQUEST
    ],
    status.HTTP_401_UNAUTHORIZED: BOOKING_RESPONSES[
        status.HTTP_401_UNAUTHORIZED
    ],
}

booking_update_responses = {
    status.HTTP_200_OK: {
        **BOOKING_RESPONSES[status.HTTP_200_OK],
        'description': 'Обновленные данные бронирования',
    },
    status.HTTP_400_BAD_REQUEST: BOOKING_RESPONSES[
        status.HTTP_400_BAD_REQUEST
    ],
    status.HTTP_401_UNAUTHORIZED: BOOKING_RESPONSES[
        status.HTTP_401_UNAUTHORIZED
    ],
    status.HTTP_404_NOT_FOUND: BOOKING_RESPONSES[
        status.HTTP_404_NOT_FOUND
    ],
}
