"""Сервис для уведомлений"""
import asyncio
from datetime import datetime, time, date
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from aiogram import Bot

from src.config import config
from src.database.base import get_db_session
from src.database.models import User, DailyFocus, UserSkill
from src.services.user_service import get_user
from src.services.skill_service import get_daily_focus


async def send_daily_reminders(bot: Bot):
    """Отправка ежедневных напоминаний"""
    async for session in get_db_session():
        # Утреннее напоминание (09:00)
        result = await session.execute(
            select(User).where(User.settings["notifications"].astext == "true")
        )
        users = list(result.scalars().all())
        
        for user in users:
            try:
                text = (
                    "🌅 Доброе утро!\n\n"
                    "Не забудьте сформировать фокус на сегодня. "
                    "Навыки в фокусе дают двойные очки! ✨"
                )
                await bot.send_message(user.telegram_id, text)
                await asyncio.sleep(0.05)  # Защита от лимитов API
            except Exception as e:
                print(f"Ошибка отправки уведомления пользователю {user.telegram_id}: {e}")


async def send_evening_reminders(bot: Bot):
    """Отправка вечерних напоминаний"""
    async for session in get_db_session():
        result = await session.execute(
            select(User).where(User.settings["notifications"].astext == "true")
        )
        users = list(result.scalars().all())
        
        for user in users:
            try:
                # Проверяем, выполнены ли навыки в фокусе
                today_focus = await get_daily_focus(session, user.id, date.today())
                
                if today_focus and today_focus.skill_ids:
                    completed_count = len(today_focus.completed_skill_ids)
                    total_count = len(today_focus.skill_ids)
                    
                    if completed_count < total_count:
                        text = (
                            "🌙 Добрый вечер!\n\n"
                            f"Подведите итоги дня! "
                            f"Выполнено навыков в фокусе: {completed_count}/{total_count}\n\n"
                            "Отметьте выполненные задания для получения очков! ✨"
                        )
                        await bot.send_message(user.telegram_id, text)
                else:
                    text = (
                        "🌙 Добрый вечер!\n\n"
                        "Подведите итоги дня! Отметьте выполненные задания."
                    )
                    await bot.send_message(user.telegram_id, text)
                
                await asyncio.sleep(0.05)
            except Exception as e:
                print(f"Ошибка отправки уведомления пользователю {user.telegram_id}: {e}")


async def send_streak_reminder(bot: Bot, user_id: int, streak_days: int):
    """Напоминание о серии"""
    try:
        text = (
            f"🔥 Ваша серия: {streak_days} дней подряд!\n\n"
            "Не прерывайте серию, продолжайте развиваться каждый день! 💪"
        )
        await bot.send_message(user_id, text)
    except Exception as e:
        print(f"Ошибка отправки напоминания о серии: {e}")


async def send_skill_completed_notification(
    bot: Bot,
    user_id: int,
    skill_title: str,
    points: int,
):
    """Уведомление о завершении навыка"""
    try:
        text = (
            f"🎉 Поздравляем!\n\n"
            f"Вы завершили навык: **{skill_title}**\n"
            f"+{points} очков\n\n"
            "Продолжайте в том же духе! 💪"
        )
        await bot.send_message(user_id, text, parse_mode="Markdown")
    except Exception as e:
        print(f"Ошибка отправки уведомления о завершении навыка: {e}")


async def send_lesson_unlocked_notification(
    bot: Bot,
    user_id: int,
    course_title: str,
    lesson_day: int,
):
    """Уведомление об открытии нового урока"""
    try:
        text = (
            f"📖 Новый урок доступен!\n\n"
            f"Курс: **{course_title}**\n"
            f"Урок {lesson_day}\n\n"
            "Продолжайте обучение! 🎓"
        )
        await bot.send_message(user_id, text, parse_mode="Markdown")
    except Exception as e:
        print(f"Ошибка отправки уведомления об уроке: {e}")


async def notification_worker(bot: Bot):
    """Рабочий поток для уведомлений"""
    while True:
        now = datetime.now()
        current_time = now.time()
        
        # Утреннее напоминание (09:00)
        if current_time.hour == 9 and current_time.minute == 0:
            await send_daily_reminders(bot)
            await asyncio.sleep(60)  # Ждем минуту, чтобы не отправлять повторно
        
        # Вечернее напоминание (20:00)
        if current_time.hour == 20 and current_time.minute == 0:
            await send_evening_reminders(bot)
            await asyncio.sleep(60)
        
        # Проверяем каждую минуту
        await asyncio.sleep(60)