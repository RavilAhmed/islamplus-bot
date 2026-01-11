"""Базовые классы для работы с БД"""
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from src.config import config

Base = declarative_base()

engine = create_async_engine(config.DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db_session():
    """Получить сессию БД (async generator)"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    """Инициализация БД (создание таблиц)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)