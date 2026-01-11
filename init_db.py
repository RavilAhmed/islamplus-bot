#!/usr/bin/env python3
"""Скрипт для инициализации базы данных"""
import asyncio
from src.database.base import init_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Инициализация БД"""
    try:
        logger.info("Инициализация базы данных...")
        await init_db()
        logger.info("База данных успешно инициализирована!")
    except Exception as e:
        logger.error(f"Ошибка инициализации БД: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())