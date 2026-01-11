"""Обработчики для Корана и лекций"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from pathlib import Path
import os

router = Router()

# Путь к папке с аудиофайлами (относительно корня проекта)
BASE_DIR = Path(__file__).parent.parent.parent
AUDIO_DIR = BASE_DIR / "tolkovanie_assaadi"

# Данные о сурах
SURAS = {
    "1": {
        "name_ar": "Аль-Фатиха",
        "name_ru": "Открывающая",
        "file": "001_Al_Fatiha.mp3",
    },
    "2": {
        "name_ar": "Аль-Бакара",
        "name_ru": "Корова",
        "file": "002_Al_Baqarah.mp3",
    },
}


@router.message(F.text == "🎧 Слушать Коран и лекции")
async def cmd_listen_quran(message: Message):
    """Меню 'Слушать Коран и лекции'"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Толкование Корана ас-Саади", callback_data="quran_assaadi")],
        ]
    )
    
    text = "🎧 **Слушать Коран и лекции**\n\nВыберите раздел:"
    
    await message.answer(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "quran_assaadi")
async def callback_quran_assaadi(callback: CallbackQuery):
    """Толкование Корана ас-Саади"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="1️⃣ Аль-Фатиха", callback_data="sura_1")],
            [InlineKeyboardButton(text="2️⃣ Аль-Бакара", callback_data="sura_2")],
        ]
    )
    
    text = "📖 **Толкование Корана ас-Саади**\n\nВыберите суру:"
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("sura_"))
async def callback_sura(callback: CallbackQuery):
    """Обработка выбора суры"""
    sura_num = callback.data.split("_")[1]
    
    if sura_num not in SURAS:
        await callback.answer("Сура не найдена", show_alert=True)
        return
    
    sura = SURAS[sura_num]
    audio_path = AUDIO_DIR / sura["file"]
    
    text = f"🎧 Сура {sura_num}\n«{sura['name_ar']}» — «{sura['name_ru']}»"
    
    if audio_path.exists():
        audio_file = FSInputFile(audio_path)
        await callback.message.delete()
        await callback.message.answer_audio(
            audio=audio_file,
            title=f"Сура {sura_num}. {sura['name_ar']}",
            performer="Толкование ас-Саади",
            caption=text,
        )
        await callback.answer()
    else:
        await callback.message.edit_text(
            f"{text}\n\n❌ Аудиофайл не найден: {audio_path}",
        )
        await callback.answer("Аудиофайл не найден", show_alert=True)


def register_quran_handlers(dp):
    """Регистрация обработчиков"""
    dp.include_router(router)