"""Утилиты для работы с БД"""
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base import async_session_maker


@asynccontextmanager
async def get_session():
    """Получить сессию БД как context manager"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise