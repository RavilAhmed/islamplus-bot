"""Обработчики для настроек"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.keyboards.main_menu import get_main_menu_keyboard

router = Router()


@router.callback_query(F.data == "menu_settings")
async def callback_menu_settings(callback: CallbackQuery):
    """Настройки"""
    text = (
        "⚙️ **Настройки**\n\n"
        "Здесь вы сможете настроить:\n"
        "🔔 Уведомления\n"
        "⏰ Время напоминаний\n"
        "🌍 Язык интерфейса\n\n"
        "Функция в разработке..."
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "menu_library")
async def callback_menu_library(callback: CallbackQuery):
    """Библиотека"""
    text = (
        "📚 **Библиотека микроконтента**\n\n"
        "Здесь будут доступны:\n"
        "📖 Статьи\n"
        "🎥 Короткие видео\n"
        "🎧 Аудио-лекции\n\n"
        "Функция в разработке..."
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


def register_settings_handlers(dp):
    """Регистрация обработчиков"""
    dp.include_router(router)