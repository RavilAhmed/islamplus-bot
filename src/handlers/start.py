"""Обработчики команд start и menu"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from src.database.base import get_db_session
from src.services.user_service import get_or_create_user
from src.keyboards.main_menu import get_main_menu_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Команда /start"""
    async for session in get_db_session():
        user = await get_or_create_user(
            session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
            language_code=message.from_user.language_code or "ru",
        )
        
        welcome_text = (
            f"Ассаляму алейкум, {user.full_name or 'друг'}! 👋\n\n"
            "Добро пожаловать в **IslamPlus.Practice** — бот для системного развития мусульманина.\n\n"
            "📚 Изучайте курсы\n"
            "🛠 Развивайте навыки и привычки\n"
            "🧠 Проверяйте знания в тестах\n"
            "📈 Отслеживайте прогресс\n\n"
            "Выберите раздел из меню:"
        )
        
        await message.answer(
            welcome_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown",
        )


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    """Команда /menu"""
    menu_text = "🏠 Главное меню:\n\nВыберите раздел:"
    await message.answer(menu_text, reply_markup=get_main_menu_keyboard())


@router.callback_query(F.data == "menu_main")
async def callback_menu_main(callback: CallbackQuery):
    """Возврат в главное меню"""
    menu_text = "🏠 Главное меню:\n\nВыберите раздел:"
    await callback.message.edit_text(menu_text, reply_markup=get_main_menu_keyboard())
    await callback.answer()


def register_start_handlers(dp):
    """Регистрация обработчиков"""
    dp.include_router(router)