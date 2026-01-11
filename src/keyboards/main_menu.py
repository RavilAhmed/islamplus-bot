"""Главное меню"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("🏁 Мои курсы", callback_data="menu_courses"),
        InlineKeyboardButton("🛠 Практика", callback_data="menu_practice"),
        InlineKeyboardButton("📚 Библиотека", callback_data="menu_library"),
        InlineKeyboardButton("🧠 Тест", callback_data="menu_test"),
        InlineKeyboardButton("📈 Прогресс", callback_data="menu_progress"),
        InlineKeyboardButton("⚙️ Настройки", callback_data="menu_settings"),
    ]
    keyboard.add(*buttons)
    return keyboard