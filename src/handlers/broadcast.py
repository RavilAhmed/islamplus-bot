"""Обработчики для рассылок (только для админов)"""
import logging
from pathlib import Path
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.config import config
from src.services.notification_service import broadcast_message

logger = logging.getLogger(__name__)

router = Router()


class BroadcastStates(StatesGroup):
    """Состояния для рассылки"""
    waiting_for_message = State()
    waiting_for_photo = State()


def is_admin(telegram_id: int) -> bool:
    """Проверка, является ли пользователь админом"""
    return telegram_id in config.ADMIN_IDS


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext):
    """Команда для начала рассылки"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для выполнения этой команды.")
        return
    
    await message.answer(
        "📢 **Рассылка сообщений**\n\n"
        "Отправьте текст сообщения, которое хотите разослать всем пользователям.\n\n"
        "Используйте HTML для форматирования:\n"
        "<b>жирный</b>, <i>курсив</i>, <code>код</code>\n\n"
        "Или отправьте /cancel для отмены.",
        parse_mode="Markdown"
    )
    await state.set_state(BroadcastStates.waiting_for_message)


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Отмена рассылки"""
    await state.clear()
    await message.answer("❌ Рассылка отменена.")


@router.message(BroadcastStates.waiting_for_message, F.photo)
async def process_broadcast_with_photo(message: Message, state: FSMContext):
    """Обработка рассылки с фото"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для выполнения этой команды.")
        await state.clear()
        return
    
    # Сохраняем фото (берем наибольшее разрешение)
    photo = message.photo[-1]
    photo_file_id = photo.file_id
    
    # Получаем текст из подписи или сообщения
    text = message.caption or "📢 Сообщение от администратора"
    
    logger.info(f"Начинаю рассылку с фото. file_id: {photo_file_id}")
    
    await message.answer(
        f"📸 **Фото получено**\n\n"
        f"Текст: {text}\n\n"
        f"Начинаю рассылку всем пользователям...",
        parse_mode="Markdown"
    )
    
    # Запускаем рассылку с file_id (проще и надежнее)
    result = await broadcast_message(
        message.bot,
        text=text,
        photo_file_id=photo_file_id
    )
    
    if result["success"]:
        await message.answer(
            f"✅ **Рассылка завершена!**\n\n"
            f"Отправлено: {result['sent']}\n"
            f"Ошибок: {result['failed']}\n"
            f"Всего пользователей: {result['total']}",
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            f"❌ **Ошибка рассылки:**\n\n{result.get('error', 'Неизвестная ошибка')}",
            parse_mode="Markdown"
        )
    
    await state.clear()


@router.message(BroadcastStates.waiting_for_message)
async def process_broadcast_text(message: Message, state: FSMContext):
    """Обработка рассылки только текста"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для выполнения этой команды.")
        await state.clear()
        return
    
    text = message.text or message.caption or "📢 Сообщение от администратора"
    
    await message.answer(
        f"📝 **Текст получен**\n\n"
        f"{text}\n\n"
        f"Начинаю рассылку всем пользователям...",
        parse_mode="Markdown"
    )
    
    # Запускаем рассылку
    result = await broadcast_message(
        message.bot,
        text=text
    )
    
    if result["success"]:
        await message.answer(
            f"✅ **Рассылка завершена!**\n\n"
            f"Отправлено: {result['sent']}\n"
            f"Ошибок: {result['failed']}\n"
            f"Всего пользователей: {result['total']}",
            parse_mode="Markdown"
        )
    else:
        await message.answer(
            f"❌ **Ошибка рассылки:**\n\n{result.get('error', 'Неизвестная ошибка')}",
            parse_mode="Markdown"
        )
    
    await state.clear()


def register_broadcast_handlers(dp):
    """Регистрация обработчиков рассылок"""
    dp.include_router(router)
