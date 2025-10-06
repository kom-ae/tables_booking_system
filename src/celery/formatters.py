def client_template_formatter(booking: dict) -> dict:
    """Формирует словарь данных для клиентского шаблона."""
    cafe: dict = booking.get('cafe', {})
    table: dict = booking.get('tables', [{}])[0]
    slot: dict = booking.get('slots', [{}])[0]
    dishes: list[dict] = booking.get('menu', [])

    menu_parts = []
    for dish in dishes:
        menu_parts.append(
            f"<div style='margin-bottom:8px;'>"
            f"<b>{dish.get('name')}</b> — {dish.get('description')} "
            f"({dish.get('price')} руб.)</div>",
        )
    menu = ''.join(menu_parts)

    return {
        'cafe_name': cafe.get('name'),
        'cafe_address': cafe.get('address'),
        'cafe_phone': cafe.get('phone'),
        'table_description': table.get('description'),
        'seats_number': table.get('seats_number'),
        'slot_date': slot.get('date'),
        'slot_start': slot.get('start_time'),
        'slot_end': slot.get('end_time'),
        'guests_number': booking.get('guests_number'),
        'menu_items': menu,
        'note': booking.get('note'),
    }


def manager_template_formatter(booking: dict) -> dict:
    """Формирует словарь данных для шаблона уведомления менеджеру."""
    user: dict = booking.get('user', {})
    cafe: dict = booking.get('cafe', {})
    table: dict = booking.get('tables', [{}])[0]
    slot: dict = booking.get('slots', [{}])[0]
    dishes: list[dict] = booking.get('menu', [])

    # собираем html для меню
    menu_parts = []
    for dish in dishes:
        menu_parts.append(
            f"<div style='margin-bottom:8px;'>"
            f"<b>{dish.get('name')}</b> — {dish.get('description')} "
            f"({dish.get('price')} руб.)</div>",
        )
    menu = ''.join(menu_parts)

    return {
        'user_username': user.get('username'),
        'user_email': user.get('email'),
        'user_phone': user.get('phone'),

        'cafe_name': cafe.get('name'),
        'cafe_address': cafe.get('address'),
        'cafe_phone': cafe.get('phone'),

        'table_description': table.get('description'),
        'seats_number': table.get('seats_number'),
        'slot_date': slot.get('date'),
        'slot_start': slot.get('start_time'),
        'slot_end': slot.get('end_time'),

        'guests_number': booking.get('guests_number'),
        'note': booking.get('note'),
        'menu_items': menu,
    }


def client_cancel_formatter(booking: dict) -> dict:
    """Контекст для отмены бронирования (клиент)."""
    return {
        'cafe_name': booking['cafe']['name'],
        'note': booking.get('note'),
    }


def manager_cancel_formatter(booking: dict) -> dict:
    """Контекст для отмены бронирования (менеджер)."""
    user = booking.get('user', {})
    return {
        'user_username': user.get('username'),
        'user_email': user.get('email'),
        'user_phone': user.get('phone'),
        'cafe_name': booking['cafe']['name'],
    }
