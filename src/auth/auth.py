import uuid

from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieTransport, AuthenticationBackend
from fastapi_users.authentication import JWTStrategy

from src.auth.userManager import get_user_manager
from src.client_profile.models import User

from src.config import SECRET


# Выбран метод передачи токена через куки
# Срок жизни такой куки 3600с или же час
cookie_transport = CookieTransport(cookie_name="messages", cookie_max_age=3600, cookie_samesite="none")

# Выбран метод хранения токена у клиента
# Срок жизни такого токена 3600с или же час
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

# Логика аутентификации
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)

# Формирование ядра FastApiUsers
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

# Получение текущей сессии
current_user = fastapi_users.current_user()