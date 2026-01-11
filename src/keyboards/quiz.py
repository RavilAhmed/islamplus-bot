"""Клавиатуры для тестов"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional


def get_quiz_mode_keyboard(categories: Optional[List[str]] = None) -> InlineKeyboardMarkup:
    """Выбор режима теста"""
    buttons = [
        [InlineKeyboardButton("♾️ Бесконечный вызов", callback_data="test:infinite")],
        [InlineKeyboardButton("📅 Ежедневная викторина", callback_data="test:daily")],
    ]
    
    if categories:
        buttons.append([
            InlineKeyboardButton("📚 Тематический раунд", callback_data="test:category_menu")
        ])
    
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="menu_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_quiz_category_keyboard(categories: List[str]) -> InlineKeyboardMarkup:
    """Выбор категории теста"""
    buttons = []
    category_names = {
        "aqeedah": "Акыда",
        "fiqh": "Фикх",
        "sira": "Сира",
        "quran": "Коран",
        "ethics": "Этика",
    }
    
    row = []
    for category in categories:
        name = category_names.get(category, category.title())
        row.append(InlineKeyboardButton(name, callback_data=f"test:category:{category}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="menu_test")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_quiz_question_keyboard(
    question_id: int,
    options: List[str],
    show_explanation: bool = False,
) -> InlineKeyboardMarkup:
    """Клавиатура вопроса теста"""
    buttons = []
    
    for idx, option in enumerate(options):
        buttons.append([
            InlineKeyboardButton(
                f"{chr(65 + idx)}. {option}",
                callback_data=f"answer:{question_id}:{idx}",
            )
        ])
    
    if show_explanation:
        buttons.append([
            InlineKeyboardButton("❓ Объяснение", callback_data=f"quiz_explanation:{question_id}")
        ])
    
    buttons.append([
        InlineKeyboardButton("⏭️ Следующий вопрос", callback_data=f"quiz_next:{question_id}"),
        InlineKeyboardButton("🔙 Назад", callback_data="menu_test"),
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)