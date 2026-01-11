"""Клавиатуры для бота"""
from .main_menu import get_main_menu_keyboard
from .courses import get_courses_keyboard, get_course_detail_keyboard, get_lesson_keyboard
from .practice import get_practice_keyboard, get_skills_keyboard, get_focus_keyboard
from .quiz import get_quiz_mode_keyboard, get_quiz_question_keyboard

__all__ = [
    "get_main_menu_keyboard",
    "get_courses_keyboard",
    "get_course_detail_keyboard",
    "get_lesson_keyboard",
    "get_practice_keyboard",
    "get_skills_keyboard",
    "get_focus_keyboard",
    "get_quiz_mode_keyboard",
    "get_quiz_question_keyboard",
]