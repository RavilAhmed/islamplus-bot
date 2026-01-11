"""Точка входа бота"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.config import config
from src.database.base import init_db
from src.handlers import (
    register_start_handlers,
    register_course_handlers,
    register_practice_handlers,
    register_quiz_handlers,
    register_progress_handlers,
    register_settings_handlers,
    register_quran_handlers,
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """Главная функция"""
    # Валидация конфигурации
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Ошибка конфигурации: {e}")
        return
    
    # Инициализация БД
    try:
        logger.info("Инициализация базы данных...")
        await init_db()
        logger.info("База данных инициализирована")
    except Exception as e:
        logger.error(f"Ошибка инициализации БД: {e}")
        return
    
    # Создание бота и диспетчера
    bot_kwargs = {
        "token": config.BOT_TOKEN,
        "default": DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
    }
    # Используем локальный Bot API, если указан
    if config.BOT_API_URL:
        bot_kwargs["base_url"] = config.BOT_API_URL
        logger.info(f"Используется локальный Bot API: {config.BOT_API_URL}")
    
    bot = Bot(**bot_kwargs)
    dp = Dispatcher()
    
    # Регистрация обработчиков
    logger.info("Регистрация обработчиков...")
    register_start_handlers(dp)
    register_course_handlers(dp)
    register_practice_handlers(dp)
    register_quiz_handlers(dp)
    register_progress_handlers(dp)
    register_settings_handlers(dp)
    register_quran_handlers(dp)
    
    # Запуск бота
    logger.info("Запуск бота...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при работе бота: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())