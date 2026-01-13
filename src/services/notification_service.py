"""Сервис для уведомлений"""
import asyncio
import logging
from datetime import datetime, time, date, timedelta
from typing import List, Optional
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from aiogram import Bot
from aiogram.types import FSInputFile

from src.config import config
from src.database.base import get_db_session
from src.database.models import User, DailyFocus, UserSkill
from src.services.user_service import get_user
from src.services.skill_service import get_daily_focus

logger = logging.getLogger(__name__)


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


async def get_all_users() -> List[User]:
    """Получить всех пользователей из БД"""
    users = []
    async for session in get_db_session():
        result = await session.execute(select(User))
        users = list(result.scalars().all())
        break
    return users


async def send_fasting_reminder(bot: Bot):
    """Отправка напоминания о посте (воскресенье и среда в 6:00 МСК)"""
    try:
        # Получаем всех пользователей
        users = await get_all_users()
        
        # Путь к изображению
        base_dir = Path(__file__).parent.parent.parent
        image_path = base_dir / "images" / "islam_praktika_banner 1.jpg"
        
        # Проверяем существование изображения
        photo = None
        if image_path.exists():
            photo = FSInputFile(image_path)
        else:
            logger.warning(f"Изображение не найдено: {image_path}")
        
        sent_count = 0
        failed_count = 0
        
        for user in users:
            try:
                # Получаем имя пользователя
                name = user.full_name or user.username or "друг"
                
                # Формируем текст сообщения
                text = (
                    f"<b>#{name}, завтра желательный пост! ✨</b>\n\n"
                    "Ас-саляму алейкум!\n"
                    "Напоминаем, что завтра — день добровольного поста, который любил соблюдать Пророк ﷺ. "
                    "Это возможность получить великую награду.\n\n"
                    "<strong>Да примет Аллах наш пост! 🤲 Амин</strong>"
                )
                
                # Отправляем сообщение с фото или без
                if photo:
                    await bot.send_photo(
                        chat_id=user.telegram_id,
                        photo=photo,
                        caption=text,
                        parse_mode="HTML"
                    )
                else:
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=text,
                        parse_mode="HTML"
                    )
                
                sent_count += 1
                await asyncio.sleep(0.05)  # Защита от лимитов API (20 сообщений в секунду)
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Ошибка отправки напоминания о посте пользователю {user.telegram_id}: {e}")
                # Продолжаем отправку другим пользователям
                continue
        
        logger.info(f"Рассылка о посте завершена. Отправлено: {sent_count}, Ошибок: {failed_count}")
        
    except Exception as e:
        logger.error(f"Критическая ошибка при рассылке о посте: {e}", exc_info=True)


async def send_friday_reminder(bot: Bot):
    """Отправка напоминания о пятнице (пятница в 4:00 МСК)"""
    try:
        # Получаем всех пользователей
        users = await get_all_users()
        
        # Путь к изображению
        base_dir = Path(__file__).parent.parent.parent
        image_path = base_dir / "images" / "islam_praktika_banner 2.jpg"
        
        # Проверяем существование изображения
        photo = None
        if image_path.exists():
            photo = FSInputFile(image_path)
        else:
            logger.warning(f"Изображение не найдено: {image_path}")
        
        sent_count = 0
        failed_count = 0
        
        for user in users:
            try:
                # Получаем имя пользователя
                name = user.full_name or user.username or "друг"
                
                # Формируем текст сообщения
                text = (
                    f"<b>#{name}, сегодня пятница! ✨</b>\n\n"
                    "Ас-саляму алейкум!\n"
                    "Сегодня лучший день недели, наполненный благословением и возможностью получить огромную награду и прощение.\n\n"
                    "<strong>🕌 Пятничная молитва в мечети — это обязанность каждого совершеннолетнего мужчины-мусульманина.\n\n"
                    "💧 Крайне желательно сделать полное омовение (гусль).\n\n</strong>"
                    "<strong>🤲 Желательные действия:</strong>\n"
                    "- Прийти в мечеть как можно раньше\n"
                    "- Надеть лучшую одежду и использовать благовония\n"
                    "- Направиться в мечеть пешком\n"
                    "- Прочесть суру «Аль-Кахф» (Пещера)\n"
                    "- Усерднее читать салават Пророку ﷺ\n"
                    "- Делать много дуа\n\n"
                    "❗ Важно внимательно и молча слушать хутбу, не создавать неудобств в мечети и оставить мирские дела после призыва на намаз.\n\n"
                    "<strong>Пусть Аллах примет наш намаз, простит грехи и ответит на наши мольбы в этот благословенный день! 🤲  Амин</strong>\n\n"
                    "<blockquote>«Тому, кто должным образом совершит омовение, а потом явится на пятничную молитву и станет слушать, храня молчание, простятся его прегрешения, совершённые им между этой и (предыдущей) пятничной молитвой, а также в течение ещё трёх дней, что же касается перебирающего камешки, то он занимается пустым»\n"
                    "(Муслим 857).\n\n"
                    "«Клянусь, либо люди прекратят пропускать пятничные молитвы, либо Аллах запечатает сердца их, после чего они непременно окажутся в числе пренебрегающих»\n"
                    "(Муслим 865).\n\n"
                    "«Когда кто-нибудь совершает очищение в своём доме, а потом отправляется в один из домов Аллаха для совершения чего-либо из предписанного Аллахом, за один из сделанных им шагов с него снимается (бремя) его прегрешений, а за другой степень его возвышается.»\n"
                    "(Муслим 666)\n\n"
                    "«Полное омовение в пятницу обязательно для каждого достигшего (половой) зрелости»\n"
                    "(Аль-Бухари 879)\n\n"
                    "«О те, которые уверовали! Когда призывают на намаз в пятничный день, то устремляйтесь к поминанию Аллаха и оставьте торговлю. Так будет лучше для вас, если бы вы только знали»\n"
                    "(Коран 62:9)</blockquote>"
                )
                
                # Отправляем сообщение с фото или без
                if photo:
                    await bot.send_photo(
                        chat_id=user.telegram_id,
                        photo=photo,
                        caption=text,
                        parse_mode="HTML"
                    )
                else:
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=text,
                        parse_mode="HTML"
                    )
                
                sent_count += 1
                await asyncio.sleep(0.05)  # Защита от лимитов API (20 сообщений в секунду)
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Ошибка отправки напоминания о пятнице пользователю {user.telegram_id}: {e}")
                # Продолжаем отправку другим пользователям
                continue
        
        logger.info(f"Рассылка о пятнице завершена. Отправлено: {sent_count}, Ошибок: {failed_count}")
        
    except Exception as e:
        logger.error(f"Критическая ошибка при рассылке о пятнице: {e}", exc_info=True)


async def broadcast_message(
    bot: Bot,
    text: str,
    photo_path: Optional[str] = None,
    photo_file_id: Optional[str] = None,
    parse_mode: str = "HTML"
) -> dict:
    """Ручная рассылка сообщения всем пользователям"""
    try:
        users = await get_all_users()
        
        # Приоритет: file_id > путь к файлу
        use_file_id = photo_file_id is not None
        
        if not use_file_id and photo_path:
            photo_file = Path(photo_path)
            # Преобразуем в абсолютный путь
            if not photo_file.is_absolute():
                base_dir = Path(__file__).parent.parent.parent
                photo_file = base_dir / photo_path
            
            logger.info(f"Проверка фото: {photo_file}, существует: {photo_file.exists()}")
            
            if photo_file.exists():
                photo_input = FSInputFile(photo_file)
                logger.info(f"Фото загружено из файла: {photo_file}")
            else:
                logger.warning(f"Изображение не найдено: {photo_file} (абсолютный путь)")
                logger.warning(f"Оригинальный путь: {photo_path}")
                photo_input = None
        else:
            photo_input = None
        
        sent_count = 0
        failed_count = 0
        
        for user in users:
            try:
                # Подставляем имя пользователя в текст (если есть {name})
                user_name = user.full_name or user.username or "друг"
                personalized_text = text.replace("{name}", user_name).replace("#{name}", f"#{user_name}")
                
                if use_file_id:
                    # Используем file_id напрямую (проще и надежнее)
                    await bot.send_photo(
                        chat_id=user.telegram_id,
                        photo=photo_file_id,
                        caption=personalized_text,
                        parse_mode=parse_mode
                    )
                elif photo_input:
                    # Используем файл с диска
                    await bot.send_photo(
                        chat_id=user.telegram_id,
                        photo=photo_input,
                        caption=personalized_text,
                        parse_mode=parse_mode
                    )
                else:
                    # Только текст
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=personalized_text,
                        parse_mode=parse_mode
                    )
                
                sent_count += 1
                await asyncio.sleep(0.05)
                
            except Exception as e:
                failed_count += 1
                logger.error(f"Ошибка отправки сообщения пользователю {user.telegram_id}: {e}", exc_info=True)
                continue
        
        return {
            "success": True,
            "sent": sent_count,
            "failed": failed_count,
            "total": len(users)
        }
        
    except Exception as e:
        logger.error(f"Критическая ошибка при рассылке: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "sent": 0,
            "failed": 0,
            "total": 0
        }


def get_msk_time() -> datetime:
    """Получить текущее время в МСК (UTC+3)"""
    utc_now = datetime.utcnow()
    msk_time = utc_now + timedelta(hours=3)
    return msk_time


async def notification_worker(bot: Bot):
    """Рабочий поток для уведомлений"""
    last_fasting_sunday = None
    last_fasting_wednesday = None
    last_friday = None
    
    while True:
        try:
            # Получаем текущее время в МСК
            msk_now = get_msk_time()
            current_time = msk_now.time()
            current_weekday = msk_now.weekday()  # 0=понедельник, 4=пятница, 6=воскресенье
            
            # Утреннее напоминание (09:00 МСК = 06:00 UTC)
            if current_time.hour == 9 and current_time.minute == 0:
                await send_daily_reminders(bot)
                await asyncio.sleep(60)
            
            # Вечернее напоминание (20:00 МСК = 17:00 UTC)
            if current_time.hour == 20 and current_time.minute == 0:
                await send_evening_reminders(bot)
                await asyncio.sleep(60)
            
            # Напоминание о посте: воскресенье в 18:00 МСК (15:00 UTC)
            if current_weekday == 6 and current_time.hour == 18 and current_time.minute == 0:
                if last_fasting_sunday != msk_now.date():
                    await send_fasting_reminder(bot)
                    last_fasting_sunday = msk_now.date()
                    await asyncio.sleep(60)
            
            # Напоминание о посте: среда в 18:00 МСК (15:00 UTC)
            if current_weekday == 2 and current_time.hour == 18 and current_time.minute == 0:
                if last_fasting_wednesday != msk_now.date():
                    await send_fasting_reminder(bot)
                    last_fasting_wednesday = msk_now.date()
                    await asyncio.sleep(60)
            
            # Напоминание о пятнице: пятница в 4:00 МСК (1:00 UTC)
            if current_weekday == 4 and current_time.hour == 4 and current_time.minute == 0:
                if last_friday != msk_now.date():
                    await send_friday_reminder(bot)
                    last_friday = msk_now.date()
                    await asyncio.sleep(60)
            
            # Проверяем каждую минуту
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Ошибка в notification_worker: {e}", exc_info=True)
            await asyncio.sleep(60)