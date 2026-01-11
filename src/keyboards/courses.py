"""Клавиатуры для курсов"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List

from src.database.models import Course, Lesson


def get_courses_keyboard(courses: List[Course], back_button: bool = False) -> InlineKeyboardMarkup:
    """Список курсов"""
    buttons = []
    
    for course in courses:
        icon = course.icon or "📖"
        button_text = f"{icon} {course.title}"
        buttons.append([InlineKeyboardButton(button_text, callback_data=f"course:{course.id}")])
    
    if back_button:
        buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="menu_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_course_detail_keyboard(course_id: int, is_started: bool = False) -> InlineKeyboardMarkup:
    """Детали курса"""
    buttons = []
    
    if is_started:
        buttons.append([InlineKeyboardButton("📖 Продолжить", callback_data=f"course_continue:{course_id}")])
    else:
        buttons.append([InlineKeyboardButton("▶️ Начать курс", callback_data=f"start_course:{course_id}")])
    
    buttons.append([
        InlineKeyboardButton("🔙 Назад", callback_data="menu_courses"),
        InlineKeyboardButton("📋 Описание", callback_data=f"course_desc:{course_id}"),
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_lesson_keyboard(lesson_id: int, course_id: int, is_completed: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура урока"""
    buttons = []
    
    if not is_completed:
        buttons.append([InlineKeyboardButton("✅ Изучил", callback_data=f"lesson_studied:{lesson_id}")])
    
    buttons.append([
        InlineKeyboardButton("🔙 К курсу", callback_data=f"course:{course_id}"),
        InlineKeyboardButton("📋 Вопросы", callback_data=f"lesson_quiz:{lesson_id}"),
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)