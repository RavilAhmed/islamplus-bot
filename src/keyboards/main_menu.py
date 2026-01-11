"""Главное меню"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню"""
    buttons = [
        [InlineKeyboardButton(text="🏁 Мои курсы", callback_data="menu_courses")],
        [InlineKeyboardButton(text="🛠 Практика", callback_data="menu_practice")],
        [InlineKeyboardButton(text="📚 Библиотека", callback_data="menu_library")],
        [InlineKeyboardButton(text="🧠 Тест", callback_data="menu_test")],
        [InlineKeyboardButton(text="📈 Прогресс", callback_data="menu_progress")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="menu_settings")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard