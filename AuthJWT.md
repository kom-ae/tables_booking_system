## Авторизация в Tables Booking System

### 1. Общая схема авторизации

1. Пользователь отправляет запрос на `/api/v1/auth/login` с email или телефоном и паролем.
2. Сервер проверяет пользователя через CRUD (`get_user_by_name`).
3. Пароль проверяется с помощью `PasswordService.verify_password`.
4. Если пароль валиден, создается JWT-токен через `TokenService.create_access_token`.
5. JWT возвращается клиенту.
6. Для последующих запросов пользователь добавляет токен в заголовок Authorization.
7. Dependency `current_user` проверяет валидность токена и возвращает пользователя.
8. Опциональные dependencies (`current_admin`, `current_manager`) проверяют права.

### 2. Ключевые компоненты

#### core/users.py
- **get_current_user_logic**:
  - Декодирует токен
  - Проверяет срок действия
  - Ищет пользователя в базе
  - Обновляет `last_used`
  - Обрабатывает ошибки (`InvalidTokenException`, `ExpiredTokenException`, `UserNotFoundException`)

- **get_user_by_name**:
  - Ищет пользователя по имени/email/телефону
  - Логирует результат поиска

#### api/endpoints/auth.py
- **login**:
  - Получает пользователя через `get_user_by_name`
  - Проверяет пароль (`PasswordService.verify_password`)
  - Обновляет `last_used`
  - Генерирует JWT через `TokenService.create_access_token`

- **logout**:
  - Информативно завершает сессию
  - JWT остаётся валидным (статический)

#### core/dependencies.py
- **current_user**:
  - Получает токен из заголовка
  - Валидирует через `get_current_user_logic`
  - Обновляет `last_used`, если прошло больше MIN_UPDATE_INTERVAL_SECONDS
  - Сохраняет данные пользователя в `request.state` для логов

- **current_admin** / **current_manager**:
  - Проверка прав пользователя
  - Генерация исключения `PermissionDeniedException` при отсутствии прав

- **get_current_user_or_none**:
  - Опциональная аутентификация
  - Возвращает пользователя если токен валиден, иначе None

#### services/auth.py
- **PasswordService**:
  - `hash_password` — создание хэша пароля
  - `verify_password` — проверка пароля
  - `dummy_verify` — защита от timing attacks

- **TokenService**:
  - `create_access_token` — создание JWT
  - В payload: `sub` (user_id), `exp`, `iat`, `last_used`

### 3. Исключения
- `InvalidTokenException` — токен поврежден или недействителен
- `ExpiredTokenException` — токен просрочен
- `UserNotFoundException` — пользователь не найден
- `PermissionDeniedException` — недостаточно прав
- `InvalidCredentialsException` — неправильный пароль

### 4. Примеры API-запросов

**Регистрация:**
```http
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "string123",
  "phone": "+79991234567",
  "username": "John Doe"
}
```

**Авторизация:**
```http
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "string123"
}
```
**Ответ:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI..."
}
```

### 5. Логирование
- Все ключевые действия (логин, декод токена, обновление last_used, ошибки) логируются через `logger`

### 6. Потоки данных JWT
```
[Client] -> /login -> [PasswordService.verify_password] -> [TokenService.create_access_token] -> JWT
[Client] -> Auth Header (Bearer JWT) -> /endpoint -> current_user -> get_current_user_logic -> User
```

### 7. Вывод
Авторизация реализована через JWT, что позволяет безопасно идентифицировать пользователя и ограничивать доступ к ресурсам по ролям. Пароли хранятся в виде хэшей (bcrypt). Ошибки корректно обрабатываются и логируются.
