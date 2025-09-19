from fastapi import Query


def parse_bool(value: str | None = Query(None, alias='show_all')) -> bool:
    """Парсинг query-параметра в bool."""
    if value is None:
        return False  # дефолт = только активные
    return value.lower() in ('1', 'true', 'yes')
