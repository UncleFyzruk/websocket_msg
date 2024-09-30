from typing import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeMeta, declarative_base

from src.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# Создание базового класса для ORM моделей
# В дальнейшем используется для определения моделей таблиц
Base: DeclarativeMeta = declarative_base()

# Объект для хранения метаданных всех таблиц
metadata = MetaData()

# Асинхронный Движок отвечает за подключение к бд
# и выполнения SQL-запросов
engine = create_async_engine(DATABASE_URL)

# Создание фабрики асинхронных сессий.
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

# Создание и возвращает сессию для работы с бд
# Также корректно открывает и закрывает сессию.
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
