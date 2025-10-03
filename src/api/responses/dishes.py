from fastapi import status

from src.api.responses.constants import DISH_RESPONSES
from src.schemas.dish import Dish

dishes_list_responses = {
    status.HTTP_200_OK: {
        'description': 'Список блюд',
        'model': list[Dish],
    },
    status.HTTP_400_BAD_REQUEST: DISH_RESPONSES[status.HTTP_400_BAD_REQUEST],
    status.HTTP_401_UNAUTHORIZED: DISH_RESPONSES[status.HTTP_401_UNAUTHORIZED],
}

dish_create_responses = {
    status.HTTP_201_CREATED: DISH_RESPONSES[status.HTTP_201_CREATED],
    status.HTTP_400_BAD_REQUEST: DISH_RESPONSES[status.HTTP_400_BAD_REQUEST],
    status.HTTP_401_UNAUTHORIZED: DISH_RESPONSES[status.HTTP_401_UNAUTHORIZED],
}

dish_get_responses = {
    status.HTTP_200_OK: DISH_RESPONSES[status.HTTP_200_OK],
    status.HTTP_401_UNAUTHORIZED: DISH_RESPONSES[status.HTTP_401_UNAUTHORIZED],
    status.HTTP_404_NOT_FOUND: DISH_RESPONSES[status.HTTP_404_NOT_FOUND],
}

dish_update_responses = {
    status.HTTP_200_OK: DISH_RESPONSES[status.HTTP_200_OK],
    status.HTTP_400_BAD_REQUEST: DISH_RESPONSES[status.HTTP_400_BAD_REQUEST],
    status.HTTP_401_UNAUTHORIZED: DISH_RESPONSES[status.HTTP_401_UNAUTHORIZED],
    status.HTTP_404_NOT_FOUND: DISH_RESPONSES[status.HTTP_404_NOT_FOUND],
}

dish_check_duplicate_responses = {
    'status_code': status.HTTP_400_BAD_REQUEST,
    'detail': 'Блюдо с таким названием в этом кафе уже существует.',
}

dish_not_found = {
    'status_code': status.HTTP_404_NOT_FOUND,
    'detail': 'Блюдо не найдено.',
}
