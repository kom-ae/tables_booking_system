from fastapi import status

from src.api.responses.constants import CAFE_RESPONSES
from src.schemas.cafes import CafeDB

cafes_list_responses = {
    status.HTTP_200_OK: {
        'description': 'Список кафе',
        'model': list[CafeDB],
    },
    status.HTTP_400_BAD_REQUEST: CAFE_RESPONSES[status.HTTP_400_BAD_REQUEST],
    status.HTTP_401_UNAUTHORIZED: CAFE_RESPONSES[status.HTTP_401_UNAUTHORIZED],
}

cafe_create_responses = {
    status.HTTP_201_CREATED: CAFE_RESPONSES[status.HTTP_201_CREATED],
    status.HTTP_400_BAD_REQUEST: CAFE_RESPONSES[status.HTTP_400_BAD_REQUEST],
    status.HTTP_401_UNAUTHORIZED: CAFE_RESPONSES[status.HTTP_401_UNAUTHORIZED],
}

cafe_get_responses = {
    status.HTTP_200_OK: CAFE_RESPONSES[status.HTTP_200_OK],
    status.HTTP_401_UNAUTHORIZED: CAFE_RESPONSES[status.HTTP_401_UNAUTHORIZED],
    status.HTTP_404_NOT_FOUND: CAFE_RESPONSES[status.HTTP_404_NOT_FOUND],
}

cafe_update_responses = {
    status.HTTP_200_OK: CAFE_RESPONSES[status.HTTP_200_OK],
    status.HTTP_400_BAD_REQUEST: CAFE_RESPONSES[status.HTTP_400_BAD_REQUEST],
    status.HTTP_401_UNAUTHORIZED: CAFE_RESPONSES[status.HTTP_401_UNAUTHORIZED],
    status.HTTP_404_NOT_FOUND: CAFE_RESPONSES[status.HTTP_404_NOT_FOUND],
}

cafe_check_duplicate_responses = {
    'status_code': status.HTTP_400_BAD_REQUEST,
    'detail': 'Кафе с таким именем и адресом уже существует.',
}

cafe_not_found = {
    'status_code': status.HTTP_404_NOT_FOUND,
    'detail': 'Кафе не найдено.',
}
