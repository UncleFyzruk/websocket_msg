from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware


from src.auth.auth import auth_backend, current_user, fastapi_users
from src.auth.shemas import UserRead, UserCreate
from src.client_profile.models import User

from src.pages.router import router as router_pages
from src.chat.router import router as router_chat
from src.client_profile.router import router as router_profile
from src.auth.router import router as router_auth

"""
Библиотека FastAPI со всеми зависимостями: pip install fastapi[all]
Запустить локальный сервер: uvicorn src.main:app --reload
Библиотека для работы с базами данных и миграции: pip install sqlalchemy alembic psycopg2
Инициализация миграции базы данных: alembic init migrations
Ревизия(версия): alembic revision --autogenerate -m "Name commit"
Сама миграция: alembic upgrade {указываем ревизию из файла версии}
Если все сломалось alembic upgrade head 


Библиотека FastAPIUsers для авторизации: pip install 'fastapi-users[sqlalchemy]'
Используем асинхронный движок для PSQL: pip install asyncpg

Своя авторизация через jwt Токены pip install pyjwt[crypto]
openssl genrsa -out jwt_private.pem 2048

"""


app = FastAPI(
    title="Websoket-server"
)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # список разрешенных источников
    allow_credentials=True, # разрешение на передачи куки межу источниками
    allow_methods=["*"], # Разрешены все HTTP_методы
    allow_headers=["*"], # разрешены все заголовки
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(router_pages)
app.include_router(router_chat)
app.include_router(router_profile)
app.include_router(router_auth)


@app.get("/protected-route")
def protected_route(user: User = Depends(current_user)):
    if user == None:
        return f"poshel naxyi anonim"
    else:
        return f"Hello, {user.username}"


@app.get("/unprotected-route")
def unprotected_route():
    return f"Hello, anon"
