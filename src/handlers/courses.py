"""Обработчики для курсов"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from src.database.base import get_db_session
from src.services.course_service import (
    get_active_courses,
    get_course,
    get_lesson_by_day,
    get_lesson,
    start_course,
    get_user_course_progress,
)
from src.services.lesson_service import (
    mark_lesson_studied,
    get_lesson_quiz,
    submit_quiz_answer,
    check_lesson_completion,
    unlock_next_lesson_after_completion,
    get_user_lesson_progress,
)
from src.services.user_service import get_user
from src.keyboards.courses import (
    get_courses_keyboard, 
    get_course_detail_keyboard, 
    get_lesson_keyboard,
    get_quiz_keyboard,
    get_quiz_result_keyboard,
)

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
                content = lesson.text_content
                if len(content) > 3000:
                    content = content[:3000] + "\n\n... (текст продолжается)"
                text += f"{content}\n\n"
            
            await callback.message.edit_text(
                text,
                reply_markup=get_lesson_keyboard(lesson.id, course_id, False, False),
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
            # Проверяем прогресс по уроку
            lesson_progress = await get_user_lesson_progress(
                session, user.id, lesson.id
            )
            is_studied = lesson_progress and lesson_progress.status != "not_started"
            is_completed = lesson_progress and lesson_progress.status == "completed"
            
            text = (
                f"📖 Урок {progress.current_lesson_day}: **{lesson.title}**\n\n"
            )
            
            if lesson.content_url:
                text += f"🎥 Видео: {lesson.content_url}\n\n"
            if lesson.text_content:
                # Ограничиваем длину текста (Telegram лимит ~4096 символов)
                content = lesson.text_content
                if len(content) > 3000:
                    content = content[:3000] + "\n\n... (текст продолжается)"
                text += f"{content}\n\n"
            
            if is_studied:
                text += "✅ Урок изучен\n"
            if is_completed:
                text += "🎉 Урок завершен!\n"
            
            await callback.message.edit_text(
                text,
                reply_markup=get_lesson_keyboard(lesson.id, course_id, is_completed),
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
    """Урок изучен - переход к тесту"""
    lesson_id = int(callback.data.split(":")[1])
    
    async for session in get_db_session():
        user = await get_user(session, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return
        
        # Отмечаем урок как изученный
        await mark_lesson_studied(session, user.id, lesson_id)
        
        # Проверяем, есть ли тест
        quiz_data = await get_lesson_quiz(session, lesson_id)
        
        if quiz_data and quiz_data.get("questions"):
            # Переходим к тесту
            questions = quiz_data["questions"]
            if questions:
                question = questions[0]
                text = (
                    f"📝 **Тест по уроку**\n\n"
                    f"Вопрос 1 из {len(questions)}:\n\n"
                    f"**{question.get('question', 'Вопрос')}**\n\n"
                )
                
                options = question.get("options", [])
                for i, option in enumerate(options):
                    text += f"{i + 1}. {option}\n"
                
                await callback.message.edit_text(
                    text,
                    reply_markup=get_quiz_keyboard(lesson_id, 0, len(questions)),
                    parse_mode="Markdown",
                )
                await callback.answer("Переход к тесту")
                return
        
        # Если теста нет, просто отмечаем как изученный
        await callback.answer("Урок отмечен как изученный! ✅")
        
        text = callback.message.text or ""
        text += "\n\n✅ Вы изучили этот урок!"
        await callback.message.edit_text(
            text, 
            reply_markup=get_lesson_keyboard(lesson_id, 0, False)
        )


@router.callback_query(F.data.startswith("lesson_quiz_start:"))
async def callback_lesson_quiz_start(callback: CallbackQuery):
    """Начать тест по уроку"""
    lesson_id = int(callback.data.split(":")[1])
    
    async for session in get_db_session():
        quiz_data = await get_lesson_quiz(session, lesson_id)
        
        if not quiz_data or not quiz_data.get("questions"):
            await callback.answer("Тест для этого урока не найден", show_alert=True)
            return
        
        questions = quiz_data["questions"]
        question = questions[0]
        
        text = (
            f"📝 **Тест по уроку**\n\n"
            f"Вопрос 1 из {len(questions)}:\n\n"
            f"**{question.get('question', 'Вопрос')}**\n\n"
        )
        
        options = question.get("options", [])
        for i, option in enumerate(options):
            text += f"{i + 1}. {option}\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_quiz_answer_keyboard(lesson_id, 0, len(questions), len(options)),
            parse_mode="Markdown",
        )
        await callback.answer()


@router.callback_query(F.data.startswith("quiz_answer:"))
async def callback_quiz_answer(callback: CallbackQuery):
    """Ответ на вопрос теста"""
    parts = callback.data.split(":")
    lesson_id = int(parts[1])
    question_index = int(parts[2])
    answer_index = int(parts[3])
    
    async for session in get_db_session():
        user = await get_user(session, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return
        
        # Отправляем ответ
        result = await submit_quiz_answer(
            session, user.id, lesson_id, question_index, answer_index
        )
        
        if "error" in result:
            await callback.answer(result["error"], show_alert=True)
            return
        
        # Получаем данные теста для следующего вопроса
        quiz_data = await get_lesson_quiz(session, lesson_id)
        questions = quiz_data.get("questions", [])
        next_question_index = question_index + 1
        
        # Формируем текст результата
        if result["correct"]:
            text = f"✅ **Правильно!**\n\n"
        else:
            text = f"❌ **Неправильно**\n\n"
        
        if result.get("explanation"):
            text += f"💡 {result['explanation']}\n\n"
        
        text += f"📊 Ваш результат: {result['score']}% ({result['correct_answers']}/{result['total_questions']})\n\n"
        
        if result["passed"]:
            text += "🎉 **Тест пройден!**\n\nТеперь можно перейти к практическим заданиям."
        elif next_question_index < len(questions):
            text += f"➡️ Переходим к следующему вопросу..."
        else:
            text += "❌ Тест не пройден. Нужно набрать минимум 70% правильных ответов."
        
        # Получаем курс для клавиатуры
        lesson = await get_lesson(session, lesson_id)
        course_id = lesson.course_id if lesson else 0
        
        await callback.message.edit_text(
            text,
            reply_markup=get_quiz_result_keyboard(
                lesson_id, 
                course_id, 
                result["passed"],
                next_question_index if next_question_index < len(questions) else None,
                len(questions)
            ),
            parse_mode="Markdown",
        )
        
        if result["correct"]:
            await callback.answer("✅ Правильно!")
        else:
            await callback.answer("❌ Неправильно")


@router.callback_query(F.data.startswith("lesson_quiz_question:"))
async def callback_lesson_quiz_question(callback: CallbackQuery):
    """Показать следующий вопрос теста"""
    parts = callback.data.split(":")
    lesson_id = int(parts[1])
    question_index = int(parts[2])
    
    async for session in get_db_session():
        quiz_data = await get_lesson_quiz(session, lesson_id)
        
        if not quiz_data or not quiz_data.get("questions"):
            await callback.answer("Тест не найден", show_alert=True)
            return
        
        questions = quiz_data["questions"]
        
        if question_index >= len(questions):
            await callback.answer("Вопрос не найден", show_alert=True)
            return
        
        question = questions[question_index]
        
        text = (
            f"📝 **Тест по уроку**\n\n"
            f"Вопрос {question_index + 1} из {len(questions)}:\n\n"
            f"**{question.get('question', 'Вопрос')}**\n\n"
        )
        
        options = question.get("options", [])
        for i, option in enumerate(options):
            text += f"{i + 1}. {option}\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_quiz_answer_keyboard(lesson_id, question_index, len(questions), len(options)),
            parse_mode="Markdown",
        )
        await callback.answer()


@router.callback_query(F.data.startswith("lesson_practice:"))
async def callback_lesson_practice(callback: CallbackQuery):
    """Переход к практическим заданиям"""
    lesson_id = int(callback.data.split(":")[1])
    
    async for session in get_db_session():
        lesson = await get_lesson(session, lesson_id)
        if not lesson:
            await callback.answer("Урок не найден", show_alert=True)
            return
        
        text = (
            f"🛠 **Практические задания**\n\n"
            f"Для завершения урока выполните практические задания.\n\n"
            f"Перейдите в раздел **Практика** и найдите задания для этого урока."
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_lesson_keyboard(lesson_id, lesson.course_id, False, True),
            parse_mode="Markdown",
        )
        await callback.answer("Перейдите в раздел Практика")


@router.callback_query(F.data.startswith("lesson:"))
async def callback_lesson_view(callback: CallbackQuery):
    """Просмотр урока по ID"""
    lesson_id = int(callback.data.split(":")[1])
    
    async for session in get_db_session():
        user = await get_user(session, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return
        
        lesson = await get_lesson(session, lesson_id)
        if not lesson:
            await callback.answer("Урок не найден", show_alert=True)
            return
        
        # Проверяем прогресс
        lesson_progress = await get_user_lesson_progress(session, user.id, lesson_id)
        is_studied = lesson_progress and lesson_progress.status != "not_started"
        is_completed = lesson_progress and lesson_progress.status == "completed"
        
        text = (
            f"📖 Урок {lesson.day_number}: **{lesson.title}**\n\n"
        )
        
        if lesson.content_url:
            text += f"🎥 Видео: {lesson.content_url}\n\n"
        if lesson.text_content:
            content = lesson.text_content
            if len(content) > 3000:
                content = content[:3000] + "\n\n... (текст продолжается)"
            text += f"{content}\n\n"
        
        if is_studied:
            text += "✅ Урок изучен\n"
        if is_completed:
            text += "🎉 Урок завершен!\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_lesson_keyboard(lesson_id, lesson.course_id, is_completed, is_studied),
            parse_mode="Markdown",
        )
        await callback.answer()


def register_course_handlers(dp):
    """Регистрация обработчиков"""
    dp.include_router(router)