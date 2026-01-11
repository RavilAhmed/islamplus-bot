"""Обработчики для курсов"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from src.database.base import get_db_session
from src.services.course_service import (
    get_active_courses,
    get_course,
    get_lesson_by_day,
    start_course,
    get_user_course_progress,
)
from src.services.user_service import get_user
from src.keyboards.courses import get_courses_keyboard, get_course_detail_keyboard, get_lesson_keyboard

router = Router()


@router.message(F.text == "🏁 Мои курсы")
async def cmd_menu_courses(message: Message):
    """Список курсов (текстовая кнопка)"""
    async for session in get_db_session():
        courses = await get_active_courses(session)
        
        if not courses:
            await message.answer(
                "📚 Курсы\n\nК сожалению, пока нет доступных курсов.",
                reply_markup=get_courses_keyboard([], back_button=True),
            )
            return
        
        text = "📚 **Доступные курсы:**\n\nВыберите курс для изучения:"
        await message.answer(
            text,
            reply_markup=get_courses_keyboard(courses, back_button=True),
            parse_mode="Markdown",
        )


@router.callback_query(F.data == "menu_courses")
async def callback_menu_courses(callback: CallbackQuery):
    """Список курсов"""
    async for session in get_db_session():
        courses = await get_active_courses(session)
        
        if not courses:
            await callback.message.edit_text(
                "📚 Курсы\n\nК сожалению, пока нет доступных курсов.",
                reply_markup=get_courses_keyboard([], back_button=True),
            )
            await callback.answer()
            return
        
        text = "📚 **Доступные курсы:**\n\nВыберите курс для изучения:"
        await callback.message.edit_text(
            text,
            reply_markup=get_courses_keyboard(courses, back_button=True),
            parse_mode="Markdown",
        )
        await callback.answer()


@router.callback_query(F.data.startswith("course:"))
async def callback_course_detail(callback: CallbackQuery):
    """Детали курса"""
    course_id = int(callback.data.split(":")[1])
    
    async for session in get_db_session():
        course = await get_course(session, course_id)
        
        if not course:
            await callback.answer("Курс не найден", show_alert=True)
            return
        
        user = await get_user(session, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return
        
        progress = await get_user_course_progress(session, user.id, course_id)
        is_started = progress is not None and progress.status == "active"
        
        icon = course.icon or "📖"
        text = (
            f"{icon} **{course.title}**\n\n"
            f"{course.description or 'Описание отсутствует'}\n\n"
            f"📅 Длительность: {course.total_days} дней\n"
            f"⭐ Сложность: {'⭐' * course.difficulty_level}\n"
            f"📚 Уроков: {course.total_days}"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_course_detail_keyboard(course_id, is_started),
            parse_mode="Markdown",
        )
        await callback.answer()


@router.callback_query(F.data.startswith("start_course:"))
async def callback_start_course(callback: CallbackQuery):
    """Начать курс"""
    course_id = int(callback.data.split(":")[1])
    
    async for session in get_db_session():
        user = await get_user(session, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return
        
        progress = await start_course(session, user.id, course_id)
        course = await get_course(session, course_id)
        
        # Получаем первый урок
        lesson = await get_lesson_by_day(session, course_id, 1)
        
        if lesson:
            text = (
                f"✅ Курс **{course.title}** начат!\n\n"
                f"📖 Урок 1: **{lesson.title}**\n\n"
            )
            
            if lesson.content_url:
                text += f"🎥 Видео: {lesson.content_url}\n\n"
            if lesson.text_content:
                text += f"{lesson.text_content}\n\n"
            
            await callback.message.edit_text(
                text,
                reply_markup=get_lesson_keyboard(lesson.id, course_id),
                parse_mode="Markdown",
            )
        else:
            await callback.message.edit_text(
                f"✅ Курс **{course.title}** начат!",
                reply_markup=get_course_detail_keyboard(course_id, is_started=True),
                parse_mode="Markdown",
            )
        
        await callback.answer("Курс начат! 🎉")


@router.callback_query(F.data.startswith("course_continue:"))
async def callback_continue_course(callback: CallbackQuery):
    """Продолжить курс"""
    course_id = int(callback.data.split(":")[1])
    
    async for session in get_db_session():
        user = await get_user(session, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return
        
        progress = await get_user_course_progress(session, user.id, course_id)
        
        if not progress:
            await callback.answer("Прогресс не найден", show_alert=True)
            return
        
        course = await get_course(session, course_id)
        lesson = await get_lesson_by_day(session, course_id, progress.current_lesson_day)
        
        if lesson:
            text = (
                f"📖 Урок {progress.current_lesson_day}: **{lesson.title}**\n\n"
            )
            
            if lesson.content_url:
                text += f"🎥 Видео: {lesson.content_url}\n\n"
            if lesson.text_content:
                text += f"{lesson.text_content}\n\n"
            
            await callback.message.edit_text(
                text,
                reply_markup=get_lesson_keyboard(lesson.id, course_id),
                parse_mode="Markdown",
            )
        else:
            await callback.message.edit_text(
                f"✅ Курс **{course.title}** завершен!",
                reply_markup=get_course_detail_keyboard(course_id, is_started=True),
                parse_mode="Markdown",
            )
        
        await callback.answer()


@router.callback_query(F.data.startswith("lesson_studied:"))
async def callback_lesson_studied(callback: CallbackQuery):
    """Урок изучен"""
    lesson_id = int(callback.data.split(":")[1])
    
    # Здесь можно добавить логику для обработки изучения урока
    # Например, задать вопросы или открыть связанные навыки
    
    await callback.answer("Урок отмечен как изученный! ✅")
    
    # Обновляем клавиатуру
    text = callback.message.text or ""
    text += "\n\n✅ Вы изучили этот урок!"
    await callback.message.edit_text(text, reply_markup=callback.message.reply_markup)


def register_course_handlers(dp):
    """Регистрация обработчиков"""
    dp.include_router(router)