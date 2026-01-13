"""Обработчики сообщений"""
from .start import register_start_handlers
from .courses import register_course_handlers
from .practice import register_practice_handlers
from .quiz import register_quiz_handlers
from .progress import register_progress_handlers
from .settings import register_settings_handlers
from .quran import register_quran_handlers
from .broadcast import register_broadcast_handlers

__all__ = [
    "register_start_handlers",
    "register_course_handlers",
    "register_practice_handlers",
    "register_quiz_handlers",
    "register_progress_handlers",
    "register_settings_handlers",
    "register_quran_handlers",
    "register_broadcast_handlers",
]