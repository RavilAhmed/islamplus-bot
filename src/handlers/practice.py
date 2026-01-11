"""Обработчики для практики"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from datetime import date

from src.database.base import get_db_session
from src.services.user_service import get_user
from src.services.skill_service import (
    get_active_user_skills,
    complete_skill,
    get_daily_focus,
    set_daily_focus,
)
from src.keyboards.practice import get_practice_keyboard, get_skills_keyboard, get_focus_keyboard

router = Router()


@router.message(F.text == "🛠 Практика")
async def cmd_menu_practice(message: Message):
    """Главное меню практики (текстовая кнопка)"""
    text = (
        "🛠 **Практика**\n\n"
        "Развивайте навыки и формируйте полезные привычки.\n\n"
        "🎯 **Сегодняшний фокус** — выберите до 5 навыков для ежедневной практики\n"
        "📋 **Мои навыки** — список всех ваших навыков\n"
        "➕ **Добавить навык** — выбрать новый навык из каталога"
    )
    
    await message.answer(
        text,
        reply_markup=get_practice_keyboard(),
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "menu_practice")
async def callback_menu_practice(callback: CallbackQuery):
    """Главное меню практики"""
    text = (
        "🛠 **Практика**\n\n"
        "Развивайте навыки и формируйте полезные привычки.\n\n"
        "🎯 **Сегодняшний фокус** — выберите до 5 навыков для ежедневной практики\n"
        "📋 **Мои навыки** — список всех ваших навыков\n"
        "➕ **Добавить навык** — выбрать новый навык из каталога"
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_practice_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "practice_skills")
async def callback_practice_skills(callback: CallbackQuery):
    """Список навыков пользователя"""
    async for session in get_db_session():
        user = await get_user(session, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return
        
        user_skills = await get_active_user_skills(session, user.id)
        
        if not user_skills:
            text = "📋 **Мои навыки**\n\nУ вас пока нет активных навыков.\n\nДобавьте навык из раздела практики."
            await callback.message.edit_text(
                text,
                reply_markup=get_practice_keyboard(),
                parse_mode="Markdown",
            )
            await callback.answer()
            return
        
        text = "📋 **Мои навыки:**\n\nВыберите навык для выполнения:"
        await callback.message.edit_text(
            text,
            reply_markup=get_skills_keyboard(user_skills),
            parse_mode="Markdown",
        )
        await callback.answer()


@router.callback_query(F.data == "practice_focus")
async def callback_practice_focus(callback: CallbackQuery):
    """Сегодняшний фокус"""
    async for session in get_db_session():
        user = await get_user(session, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return
        
        today_focus = await get_daily_focus(session, user.id, date.today())
        user_skills = await get_active_user_skills(session, user.id)
        
        selected_ids = today_focus.skill_ids if today_focus else []
        
        text = (
            "🎯 **Сегодняшний фокус**\n\n"
            "Выберите до 5 навыков для ежедневной практики.\n"
            "Навыки в фокусе дают двойные очки! ✨\n\n"
            f"Выбрано: {len(selected_ids)}/5"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_focus_keyboard(user_skills, selected_ids),
            parse_mode="Markdown",
        )
        await callback.answer()


@router.callback_query(F.data.startswith("focus_add:"))
async def callback_focus_add(callback: CallbackQuery):
    """Добавить навык в фокус"""
    skill_id = int(callback.data.split(":")[1])
    
    async for session in get_db_session():
        user = await get_user(session, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return
        
        today_focus = await get_daily_focus(session, user.id, date.today())
        selected_ids = today_focus.skill_ids if today_focus else []
        
        if skill_id not in selected_ids:
            selected_ids.append(skill_id)
        
        user_skills = await get_active_user_skills(session, user.id)
        
        text = (
            "🎯 **Сегодняшний фокус**\n\n"
            "Выберите до 5 навыков для ежедневной практики.\n"
            "Навыки в фокусе дают двойные очки! ✨\n\n"
            f"Выбрано: {len(selected_ids)}/5"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_focus_keyboard(user_skills, selected_ids),
            parse_mode="Markdown",
        )
        await callback.answer("Навык добавлен в фокус ✨")


@router.callback_query(F.data.startswith("focus_remove:"))
async def callback_focus_remove(callback: CallbackQuery):
    """Убрать навык из фокуса"""
    skill_id = int(callback.data.split(":")[1])
    
    async for session in get_db_session():
        user = await get_user(session, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return
        
        today_focus = await get_daily_focus(session, user.id, date.today())
        selected_ids = today_focus.skill_ids if today_focus else []
        
        if skill_id in selected_ids:
            selected_ids.remove(skill_id)
        
        user_skills = await get_active_user_skills(session, user.id)
        
        text = (
            "🎯 **Сегодняшний фокус**\n\n"
            "Выберите до 5 навыков для ежедневной практики.\n"
            "Навыки в фокусе дают двойные очки! ✨\n\n"
            f"Выбрано: {len(selected_ids)}/5"
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=get_focus_keyboard(user_skills, selected_ids),
            parse_mode="Markdown",
        )
        await callback.answer("Навык убран из фокуса")


@router.callback_query(F.data == "focus_save")
async def callback_focus_save(callback: CallbackQuery):
    """Сохранить фокус"""
    async for session in get_db_session():
        user = await get_user(session, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return
        
        today_focus = await get_daily_focus(session, user.id, date.today())
        selected_ids = today_focus.skill_ids if today_focus else []
        
        try:
            await set_daily_focus(session, user.id, selected_ids)
            await callback.answer("Фокус сохранен! ✅")
            
            text = (
                "✅ **Фокус сохранен!**\n\n"
                f"Выбрано навыков: {len(selected_ids)}/5\n\n"
                "Выполняйте навыки в фокусе ежедневно для получения двойных очков! ✨"
            )
            
            await callback.message.edit_text(
                text,
                reply_markup=get_practice_keyboard(),
                parse_mode="Markdown",
            )
        except ValueError as e:
            await callback.answer(str(e), show_alert=True)


@router.callback_query(F.data.startswith("skill_complete:"))
async def callback_skill_complete(callback: CallbackQuery):
    """Выполнить навык"""
    skill_id = int(callback.data.split(":")[1])
    
    async for session in get_db_session():
        user = await get_user(session, callback.from_user.id)
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return
        
        result = await complete_skill(session, user.id, skill_id)
        
        if result.success:
            message = f"+{result.points} очков! ✨"
            if result.completed:
                message += "\n🎉 Навык завершен!"
            await callback.answer(message, show_alert=True)
            
            # Обновляем список навыков
            user_skills = await get_active_user_skills(session, user.id)
            text = "📋 **Мои навыки:**\n\nВыберите навык для выполнения:"
            await callback.message.edit_text(
                text,
                reply_markup=get_skills_keyboard(user_skills),
                parse_mode="Markdown",
            )
        else:
            await callback.answer(result.message, show_alert=True)


def register_practice_handlers(dp):
    """Регистрация обработчиков"""
    dp.include_router(router)