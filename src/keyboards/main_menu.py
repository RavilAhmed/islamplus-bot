"""Главное меню"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню (обычная клавиатура)"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏁 Мои курсы")],
            [KeyboardButton(text="🛠 Практика")],
            [KeyboardButton(text="🎧 Слушать Коран и лекции")],
            [KeyboardButton(text="📚 Библиотека")],
            [KeyboardButton(text="🧠 Тест")],
            [KeyboardButton(text="📈 Прогресс")],
            [KeyboardButton(text="⚙️ Настройки")],
        ],
        resize_keyboard=True,
    )
    return keyboard


def remove_keyboard() -> ReplyKeyboardRemove:
    """Убрать клавиатуру"""
    return ReplyKeyboardRemove()