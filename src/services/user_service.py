"""Сервис для работы с пользователями"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional
from datetime import datetime

from src.database.models import User
from src.config import config


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: Optional[str] = None,
    full_name: Optional[str] = None,
    language_code: str = "ru",
) -> User:
    """Получить или создать пользователя"""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
            language_code=language_code,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    
    return user


async def get_user(session: AsyncSession, telegram_id: int) -> Optional[User]:
    """Получить пользователя по telegram_id"""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    return result.scalar_one_or_none()


async def add_points(session: AsyncSession, user: User, points: int) -> User:
    """Добавить очки пользователю"""
    user.points += points
    await session.commit()
    await session.refresh(user)
    return user


async def update_streak(session: AsyncSession, user: User, increment: bool = True) -> User:
    """Обновить серию пользователя"""
    if increment:
        user.current_streak += 1
        if user.current_streak > user.longest_streak:
            user.longest_streak = user.current_streak
    else:
        user.current_streak = 0
    
    await session.commit()
    await session.refresh(user)
    return user


async def is_admin(telegram_id: int) -> bool:
    """Проверить, является ли пользователь администратором"""
    return telegram_id in config.ADMIN_IDS