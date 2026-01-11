"""Конфигурация приложения"""
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Конфигурация бота"""
    
    # Telegram
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    
    # База данных
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://user:password@localhost:5432/islamplus"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Администраторы
    ADMIN_IDS: List[int] = [
        int(admin_id.strip())
        for admin_id in os.getenv("ADMIN_IDS", "").split(",")
        if admin_id.strip()
    ]
    
    # Настройки системы
    DAILY_FOCUS_LIMIT: int = int(os.getenv("DAILY_FOCUS_LIMIT", "5"))
    POINTS_MULTIPLIER_FOCUS: float = float(os.getenv("POINTS_MULTIPLIER_FOCUS", "2"))
    COMBO_BONUS_POINTS: int = int(os.getenv("COMBO_BONUS_POINTS", "50"))
    MAX_STREAK_MULTIPLIER: float = float(os.getenv("MAX_STREAK_MULTIPLIER", "3.0"))
    
    # Время уведомлений (UTC)
    MORNING_REMINDER: str = os.getenv("MORNING_REMINDER", "06:00")
    EVENING_REMINDER: str = os.getenv("EVENING_REMINDER", "17:00")
    DAILY_REMINDER: str = os.getenv("DAILY_REMINDER", "20:00")
    
    @classmethod
    def validate(cls) -> bool:
        """Проверка обязательных параметров"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не установлен в .env файле")
        return True


config = Config()