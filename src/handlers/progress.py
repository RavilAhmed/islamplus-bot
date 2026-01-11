"""Обработчики для прогресса"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message

from src.database.base import get_db_session
from src.services.user_service import get_user
from src.services.course_service import get_user_course_progress, get_active_courses
from src.services.skill_service import get_active_user_skills
from src.services.quiz_service import get_user_quiz_progress
from src.keyboards.main_menu import get_main_menu_keyboard

router = Router()


@router.message(F.text == "📈 Прогресс")
async def cmd_menu_progress(message: Message):
    """Прогресс пользователя (текстовая кнопка)"""
    async for session in get_db_session():
        user = await get_user(session, message.from_user.id)
        if not user:
            await message.answer("Пользователь не найден")
            return
        
        # Получаем статистику
        user_skills = await get_active_user_skills(session, user.id)
        completed_skills = [s for s in user_skills if s.status == "completed"]
        active_skills = [s for s in user_skills if s.status == "active"]
        
        courses = await get_active_courses(session)
        active_courses_count = 0
        completed_courses_count = 0
        
        for course in courses:
            progress = await get_user_course_progress(session, user.id, course.id)
            if progress:
                if progress.status == "active":
                    active_courses_count += 1
                elif progress.status == "completed":
                    completed_courses_count += 1
        
        quiz_progress = await get_user_quiz_progress(session, user.id, "infinite")
        
        text = (
            f"📈 **Ваш прогресс**\n\n"
            f"💎 Очков: {user.points}\n"
            f"🔥 Серия: {user.current_streak} дней\n"
            f"🏆 Лучшая серия: {user.longest_streak} дней\n\n"
            f"📚 **Курсы:**\n"
            f"   Активных: {active_courses_count}\n"
            f"   Завершено: {completed_courses_count}\n\n"
            f"🛠 **Навыки:**\n"
            f"   Активных: {len(active_skills)}\n"
            f"   Завершено: {len(completed_skills)}\n\n"
        )
        
        if quiz_progress:
            accuracy = (
                (quiz_progress.total_correct / quiz_progress.total_answered * 100)
                if quiz_progress.total_answered > 0
                else 0
            )
            text += (
                f"🧠 **Тесты:**\n"
                f"   Отвечено: {quiz_progress.total_answered}\n"
                f"   Правильно: {quiz_progress.total_correct}\n"
                f"   Точность: {accuracy:.1f}%\n"
                f"   Серия: {quiz_progress.current_streak}\n"
            )
        
        await message.answer(
            text,
            parse_mode="Markdown",
        )


@router.callback_query(F.data == "menu_progress")
async def callback_menu_progress(callback: CallbackQuery):
    """Прогресс пользователя"""
    async for session in get_db_session():
        user = await get_user(session, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return
        
        # Получаем статистику
        user_skills = await get_active_user_skills(session, user.id)
        completed_skills = [s for s in user_skills if s.status == "completed"]
        active_skills = [s for s in user_skills if s.status == "active"]
        
        courses = await get_active_courses(session)
        active_courses_count = 0
        completed_courses_count = 0
        
        for course in courses:
            progress = await get_user_course_progress(session, user.id, course.id)
            if progress:
                if progress.status == "active":
                    active_courses_count += 1
                elif progress.status == "completed":
                    completed_courses_count += 1
        
        quiz_progress = await get_user_quiz_progress(session, user.id, "infinite")
        
        text = (
            f"📈 **Ваш прогресс**\n\n"
            f"💎 Очков: {user.points}\n"
            f"🔥 Серия: {user.current_streak} дней\n"
            f"🏆 Лучшая серия: {user.longest_streak} дней\n\n"
            f"📚 **Курсы:**\n"
            f"   Активных: {active_courses_count}\n"
            f"   Завершено: {completed_courses_count}\n\n"
            f"🛠 **Навыки:**\n"
            f"   Активных: {len(active_skills)}\n"
            f"   Завершено: {len(completed_skills)}\n\n"
        )
        
        if quiz_progress:
            accuracy = (
                (quiz_progress.total_correct / quiz_progress.total_answered * 100)
                if quiz_progress.total_answered > 0
                else 0
            )
            text += (
                f"🧠 **Тесты:**\n"
                f"   Отвечено: {quiz_progress.total_answered}\n"
                f"   Правильно: {quiz_progress.total_correct}\n"
                f"   Точность: {accuracy:.1f}%\n"
                f"   Серия: {quiz_progress.current_streak}\n"
            )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown",
        )
        await callback.answer()


def register_progress_handlers(dp):
    """Регистрация обработчиков"""
    dp.include_router(router)