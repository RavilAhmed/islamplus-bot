"""Клавиатуры для курсов"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List

from src.database.models import Course, Lesson


def get_courses_keyboard(courses: List[Course], back_button: bool = False) -> InlineKeyboardMarkup:
    """Список курсов"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    for course in courses:
        icon = course.icon or "📖"
        button_text = f"{icon} {course.title}"
        keyboard.add(InlineKeyboardButton(button_text, callback_data=f"course:{course.id}"))
    
    if back_button:
        keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="menu_main"))
    
    return keyboard


def get_course_detail_keyboard(course_id: int, is_started: bool = False) -> InlineKeyboardMarkup:
    """Детали курса"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    if is_started:
        keyboard.add(InlineKeyboardButton("📖 Продолжить", callback_data=f"course_continue:{course_id}"))
    else:
        keyboard.add(InlineKeyboardButton("▶️ Начать курс", callback_data=f"start_course:{course_id}"))
    
    keyboard.add(
        InlineKeyboardButton("🔙 Назад", callback_data="menu_courses"),
        InlineKeyboardButton("📋 Описание", callback_data=f"course_desc:{course_id}"),
    )
    
    return keyboard


def get_lesson_keyboard(lesson_id: int, course_id: int, is_completed: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура урока"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    if not is_completed:
        keyboard.add(InlineKeyboardButton("✅ Изучил", callback_data=f"lesson_studied:{lesson_id}"))
    
    keyboard.add(
        InlineKeyboardButton("🔙 К курсу", callback_data=f"course:{course_id}"),
        InlineKeyboardButton("📋 Вопросы", callback_data=f"lesson_quiz:{lesson_id}"),
    )
    
    return keyboard