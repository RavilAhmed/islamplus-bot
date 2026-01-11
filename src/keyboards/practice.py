"""Клавиатуры для практики"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List

from src.database.models import UserSkill


def get_practice_keyboard() -> InlineKeyboardMarkup:
    """Главное меню практики"""
    buttons = [
        [InlineKeyboardButton("🎯 Сегодняшний фокус", callback_data="practice_focus")],
        [InlineKeyboardButton("📋 Мои навыки", callback_data="practice_skills")],
        [InlineKeyboardButton("➕ Добавить навык", callback_data="practice_add")],
        [InlineKeyboardButton("🔙 Назад", callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_skills_keyboard(user_skills: List[UserSkill], show_complete: bool = False) -> InlineKeyboardMarkup:
    """Список навыков пользователя"""
    buttons = []
    
    for user_skill in user_skills:
        if user_skill.status == "completed" and not show_complete:
            continue
        
        status_icon = "✅" if user_skill.status == "completed" else "🔄"
        progress = f"{user_skill.current_streak}/{user_skill.target_streak}"
        button_text = f"{status_icon} {user_skill.skill.title} ({progress})"
        
        callback_data = f"skill_view:{user_skill.skill_id}"
        if user_skill.status == "active":
            callback_data = f"skill_complete:{user_skill.skill_id}"
        
        buttons.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="menu_practice")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_focus_keyboard(
    available_skills: List[UserSkill],
    selected_skill_ids: List[int],
    max_selection: int = 5,
) -> InlineKeyboardMarkup:
    """Выбор навыков для фокуса"""
    buttons = []
    
    for user_skill in available_skills:
        if user_skill.status != "active":
            continue
        
        is_selected = user_skill.skill_id in selected_skill_ids
        icon = "✅" if is_selected else "⚪"
        button_text = f"{icon} {user_skill.skill.title}"
        
        if is_selected:
            callback_data = f"focus_remove:{user_skill.skill_id}"
        elif len(selected_skill_ids) < max_selection:
            callback_data = f"focus_add:{user_skill.skill_id}"
        else:
            continue  # Пропускаем, если достигнут лимит
        
        buttons.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    
    buttons.append([
        InlineKeyboardButton("💾 Сохранить фокус", callback_data="focus_save"),
        InlineKeyboardButton("🔙 Назад", callback_data="menu_practice"),
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)