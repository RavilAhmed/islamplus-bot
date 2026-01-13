"""Клавиатуры для курсов"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional

from src.database.models import Course, Lesson


def get_courses_keyboard(courses: List[Course], back_button: bool = False) -> InlineKeyboardMarkup:
    """Список курсов"""
    buttons = []
    
    for course in courses:
        icon = course.icon or "📖"
        button_text = f"{icon} {course.title}"
        buttons.append([InlineKeyboardButton(text=button_text, callback_data=f"course:{course.id}")])
    
    if back_button:
        buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="menu_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_course_detail_keyboard(course_id: int, is_started: bool = False) -> InlineKeyboardMarkup:
    """Детали курса"""
    buttons = []
    
    if is_started:
        buttons.append([InlineKeyboardButton(text="📖 Продолжить", callback_data=f"course_continue:{course_id}")])
    else:
        buttons.append([InlineKeyboardButton(text="▶️ Начать курс", callback_data=f"start_course:{course_id}")])
    
    buttons.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="menu_courses"),
        InlineKeyboardButton(text="📋 Описание", callback_data=f"course_desc:{course_id}"),
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_lesson_keyboard(lesson_id: int, course_id: int, is_completed: bool = False, is_studied: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура урока"""
    buttons = []
    
    if not is_studied:
        buttons.append([InlineKeyboardButton(text="✅ Изучил урок", callback_data=f"lesson_studied:{lesson_id}")])
    elif not is_completed:
        buttons.append([InlineKeyboardButton(text="📝 Пройти тест", callback_data=f"lesson_quiz_start:{lesson_id}")])
    
    buttons.append([
        InlineKeyboardButton(text="🔙 К курсу", callback_data=f"course:{course_id}"),
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_quiz_keyboard(lesson_id: int, question_index: int, total_questions: int) -> InlineKeyboardMarkup:
    """Клавиатура для теста"""
    buttons = []
    
    # Кнопки с вариантами ответов (1, 2, 3, 4)
    # Будем создавать динамически в обработчике
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_quiz_answer_keyboard(lesson_id: int, question_index: int, total_questions: int, num_options: int) -> InlineKeyboardMarkup:
    """Клавиатура с вариантами ответов"""
    buttons = []
    
    # Создаем кнопки для каждого варианта ответа
    for i in range(num_options):
        buttons.append([
            InlineKeyboardButton(
                text=f"{i + 1}",
                callback_data=f"quiz_answer:{lesson_id}:{question_index}:{i}"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_quiz_result_keyboard(lesson_id: int, course_id: int, passed: bool, next_question_index: Optional[int] = None, total_questions: int = 0) -> InlineKeyboardMarkup:
    """Клавиатура после ответа на вопрос"""
    buttons = []
    
    if passed and next_question_index is None:
        # Тест пройден, переходим к практике
        buttons.append([InlineKeyboardButton(text="🛠 Перейти к практике", callback_data=f"lesson_practice:{lesson_id}")])
    elif next_question_index is not None and next_question_index < total_questions:
        # Следующий вопрос
        buttons.append([InlineKeyboardButton(text="➡️ Следующий вопрос", callback_data=f"lesson_quiz_question:{lesson_id}:{next_question_index}")])
    elif not passed:
        # Тест не пройден, можно попробовать снова
        buttons.append([InlineKeyboardButton(text="🔄 Попробовать снова", callback_data=f"lesson_quiz_start:{lesson_id}")])
    
    buttons.append([InlineKeyboardButton(text="🔙 К уроку", callback_data=f"lesson:{lesson_id}")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)