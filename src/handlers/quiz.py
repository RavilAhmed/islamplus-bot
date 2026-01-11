"""Обработчики для тестов"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.database.base import get_db_session
from src.services.user_service import get_user
from src.services.quiz_service import (
    get_random_question,
    answer_question,
    get_categories,
    create_or_get_quiz_progress,
)
from src.keyboards.quiz import get_quiz_mode_keyboard, get_quiz_category_keyboard, get_quiz_question_keyboard

router = Router()

# Хранение текущих вопросов для пользователей (в продакшене использовать Redis)
user_current_questions = {}


@router.callback_query(F.data == "menu_test")
async def callback_menu_test(callback: CallbackQuery):
    """Главное меню тестов"""
    async for session in get_db_session():
        categories = await get_categories(session)
        
        text = (
            "🧠 **Большой Тест**\n\n"
            "Проверьте свои знания по исламу!\n\n"
            "♾️ **Бесконечный вызов** — отвечайте на вопросы без ограничений\n"
            "📅 **Ежедневная викторина** — 5 вопросов каждый день\n"
            "📚 **Тематический раунд** — вопросы по выбранной категории"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_quiz_mode_keyboard(categories),
            parse_mode="Markdown",
        )
        await callback.answer()


@router.callback_query(F.data == "test:category_menu")
async def callback_test_category_menu(callback: CallbackQuery):
    """Меню выбора категории"""
    async for session in get_db_session():
        categories = await get_categories(session)
        
        text = "📚 **Выберите категорию:**"
        await callback.message.edit_text(
            text,
            reply_markup=get_quiz_category_keyboard(categories),
            parse_mode="Markdown",
        )
        await callback.answer()


@router.callback_query(F.data.startswith("test:"))
async def callback_test_start(callback: CallbackQuery):
    """Начать тест"""
    parts = callback.data.split(":")
    quiz_mode = parts[1]
    category = parts[2] if len(parts) > 2 else None
    
    async for session in get_db_session():
        user = await get_user(session, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return
        
        if quiz_mode == "category" and category:
            quiz_mode = f"category_{category}"
        
        question = await get_random_question(session, category)
        
        if not question:
            await callback.answer("Вопросы не найдены", show_alert=True)
            return
        
        # Сохраняем текущий вопрос
        user_id = callback.from_user.id
        user_current_questions[user_id] = {
            "question_id": question.id,
            "quiz_mode": quiz_mode,
            "category": category,
        }
        
        text = (
            f"🧠 **Вопрос**\n\n"
            f"{question.question_text}\n\n"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_quiz_question_keyboard(question.id, question.options),
            parse_mode="Markdown",
        )
        await callback.answer()


@router.callback_query(F.data.startswith("answer:"))
async def callback_answer_question(callback: CallbackQuery):
    """Ответить на вопрос"""
    parts = callback.data.split(":")
    question_id = int(parts[1])
    answer_index = int(parts[2])
    
    async for session in get_db_session():
        user = await get_user(session, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return
        
        user_id = callback.from_user.id
        current_question = user_current_questions.get(user_id, {})
        quiz_mode = current_question.get("quiz_mode", "infinite")
        
        result = await answer_question(
            session,
            user.id,
            question_id,
            answer_index,
            quiz_mode,
        )
        
        question = await get_random_question(session, current_question.get("category"))
        
        if result.correct:
            message = (
                f"✅ Правильно!\n"
                f"+{result.points} очков\n"
                f"Серия: {result.current_streak} (x{result.multiplier:.1f})"
            )
        else:
            message = "❌ Неправильно. Попробуйте еще раз!"
        
        await callback.answer(message, show_alert=True)
        
        if question:
            # Сохраняем новый вопрос
            user_current_questions[user_id] = {
                "question_id": question.id,
                "quiz_mode": quiz_mode,
                "category": current_question.get("category"),
            }
            
            text = (
                f"🧠 **Вопрос**\n\n"
                f"{question.question_text}\n\n"
            )
            
            await callback.message.edit_text(
                text,
                reply_markup=get_quiz_question_keyboard(question.id, question.options),
                parse_mode="Markdown",
            )
        else:
            await callback.message.edit_text(
                "✅ Тест завершен! Вопросы закончились.",
                reply_markup=get_quiz_mode_keyboard([]),
            )


@router.callback_query(F.data.startswith("quiz_next:"))
async def callback_quiz_next(callback: CallbackQuery):
    """Следующий вопрос"""
    user_id = callback.from_user.id
    current_question = user_current_questions.get(user_id, {})
    
    async for session in get_db_session():
        question = await get_random_question(session, current_question.get("category"))
        
        if question:
            user_current_questions[user_id] = {
                "question_id": question.id,
                "quiz_mode": current_question.get("quiz_mode", "infinite"),
                "category": current_question.get("category"),
            }
            
            text = (
                f"🧠 **Вопрос**\n\n"
                f"{question.question_text}\n\n"
            )
            
            await callback.message.edit_text(
                text,
                reply_markup=get_quiz_question_keyboard(question.id, question.options),
                parse_mode="Markdown",
            )
            await callback.answer()
        else:
            await callback.answer("Вопросы не найдены", show_alert=True)


def register_quiz_handlers(dp):
    """Регистрация обработчиков"""
    dp.include_router(router)