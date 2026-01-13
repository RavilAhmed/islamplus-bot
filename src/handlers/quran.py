"""Обработчики для Корана и лекций"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from pathlib import Path

logger = logging.getLogger(__name__)

router = Router()

# Путь к папке с аудиофайлами (относительно корня проекта)
BASE_DIR = Path(__file__).parent.parent.parent
AUDIO_DIR = BASE_DIR / "tolkovanie_assaadi"

# Данные о сурах
SURAS = {
    "1": {"name_ar": "Аль-Фатиха", "name_ru": "Открывающая", "file": "001_Al_Fatiha.mp3", "description": ""},
    "2": {"name_ar": "Аль-Бакара", "name_ru": "Корова", "file": "002_Al_Baqarah.mp3", "description": ""},
    "3": {"name_ar": "Аль-Имран", "name_ru": "Семейство Имрана", "file": "003_A'al_Imran.mp3", "description": ""},
    "4": {"name_ar": "Ан-Ниса", "name_ru": "Женщины", "file": "004_Al_Nesa'a.mp3", "description": ""},
    "5": {"name_ar": "Аль-Маида", "name_ru": "Трапеза", "file": "005_Al_Ma'edah.mp3", "description": ""},
    "6": {"name_ar": "Аль-Анам", "name_ru": "Скот", "file": "006_Al_ana'am.mp3", "description": ""},
    "7": {"name_ar": "Аль-Араф", "name_ru": "Преграды", "file": "007_ Al A`araf.mp3", "description": ""},
    "8": {"name_ar": "Аль-Анфаль", "name_ru": "Трофеи", "file": "008_Al_Anfal.mp3", "description": ""},
    "9": {"name_ar": "Ат-Тауба", "name_ru": "Покаяние", "file": "009_ At_Tawba.mp3", "description": ""},
    "10": {"name_ar": "Йунус", "name_ru": "Иона", "file": "010_Yunus.mp3", "description": ""},
    "11": {"name_ar": "Худ", "name_ru": "Худ", "file": "011_Hud.mp3", "description": ""},
    "12": {"name_ar": "Йусуф", "name_ru": "Иосиф", "file": "012_Yusuf.mp3", "description": ""},
    "13": {"name_ar": "Ар-Раад", "name_ru": "Гром", "file": "013_Ar_Rad.mp3", "description": ""},
    "14": {"name_ar": "Ибрахим", "name_ru": "Авраам", "file": "014_Ibrahim.mp3", "description": ""},
    "15": {"name_ar": "Аль-Хиджр", "name_ru": "Хиджр", "file": "015_Al_Hijr.mp3", "description": ""},
    "16": {"name_ar": "Ан-Нахль", "name_ru": "Пчёлы", "file": "016_Al_Nahl.mp3", "description": ""},
    "17": {"name_ar": "Аль-Исра", "name_ru": "Ночной перенос", "file": "017_Al_Isra.mp3", "description": ""},
    "18": {"name_ar": "Аль-Кахф", "name_ru": "Пещера", "file": "018_Al_Kahf.mp3", "description": ""},
    "19": {"name_ar": "Марьям", "name_ru": "Мария", "file": "019_Maryam.mp3", "description": ""},
    "20": {"name_ar": "Та Ха", "name_ru": "Та Ха", "file": "020_Taha.mp3", "description": ""},
    "21": {"name_ar": "Аль-Анбийа", "name_ru": "Пророки", "file": "021_Al_Anbiya.mp3", "description": ""},
    "22": {"name_ar": "Аль-Хаджж", "name_ru": "Паломничество", "file": "022_Al_Najj.mp3", "description": ""},
    "23": {"name_ar": "Аль-Муминун", "name_ru": "Верующие", "file": "023_Al_Mumenoon.mp3", "description": ""},
    "24": {"name_ar": "Ан-Нур", "name_ru": "Свет", "file": "024_An_Noor.mp3", "description": ""},
    "25": {"name_ar": "Аль-Фуркан", "name_ru": "Различение", "file": "025_Al_Furqan.mp3", "description": ""},
    "26": {"name_ar": "Аш-Шуара", "name_ru": "Поэты", "file": "026_Ash_Shuara.mp3", "description": ""},
    "27": {"name_ar": "Ан-Намль", "name_ru": "Муравьи", "file": "027_An_Naml.mp3", "description": ""},
    "28": {"name_ar": "Аль-Касас", "name_ru": "Рассказ", "file": "028_Al_Qasas.mp3", "description": ""},
    "29": {"name_ar": "Аль-Анкабут", "name_ru": "Паук", "file": "029_Al_Ankaboot.mp3", "description": ""},
    "30": {"name_ar": "Ар-Рум", "name_ru": "Римляне", "file": "030_Ar_Room.mp3", "description": ""},
    "31": {"name_ar": "Лукман", "name_ru": "Лукман", "file": "031_Luqman.mp3", "description": ""},
    "32": {"name_ar": "Ас-Саджда", "name_ru": "Поклон", "file": "032_As_Sajda.mp3", "description": ""},
    "33": {"name_ar": "Аль-Ахзаб", "name_ru": "Сонмы", "file": "033_Al_Ahzab.mp3", "description": ""},
    "34": {"name_ar": "Саба", "name_ru": "Саба", "file": "034_Saba.mp3", "description": ""},
    "35": {"name_ar": "Фатыр", "name_ru": "Ангелы", "file": "035_Fatir.mp3", "description": ""},
    "36": {"name_ar": "Ясин", "name_ru": "Йа Син", "file": "036_Yaseen.mp3", "description": ""},
    "37": {"name_ar": "Ас-Саффат", "name_ru": "Стоящие в ряд", "file": "037_AsSaaffat.mp3", "description": ""},
    "38": {"name_ar": "Сад", "name_ru": "Сад", "file": "038_Sad.mp3", "description": ""},
    "39": {"name_ar": "Аз-Зумар", "name_ru": "Толпы", "file": "039_Az_Zumar.mp3", "description": ""},
    "40": {"name_ar": "Гафир", "name_ru": "Прощающий", "file": "040_Ghafir.mp3", "description": ""},
    "41": {"name_ar": "Фуссилат", "name_ru": "Разъяснены", "file": "041_Fussilat.mp3", "description": ""},
    "42": {"name_ar": "Аш-Шура", "name_ru": "Совет", "file": "042_Ash_Shura.mp3", "description": ""},
    "43": {"name_ar": "Аз-Зухруф", "name_ru": "Украшения", "file": "043_Az_Zukhruf.mp3", "description": ""},
    "44": {"name_ar": "Ад-Духан", "name_ru": "Дым", "file": "044_Ad_Dukhan.mp3", "description": ""},
    "45": {"name_ar": "Аль-Джасия", "name_ru": "Коленопреклонённые", "file": "045_Al_Jathiya.mp3", "description": ""},
    "46": {"name_ar": "Аль-Ахкаф", "name_ru": "Пески", "file": "046_Al_Ahqaf.mp3", "description": ""},
    "47": {"name_ar": "Мухаммад", "name_ru": "Мухаммад", "file": "047_Muhammad.mp3", "description": ""},
    "48": {"name_ar": "Аль-Фатх", "name_ru": "Победа", "file": "048_Al_Fath.mp3", "description": ""},
    "49": {"name_ar": "Аль-Худжурат", "name_ru": "Комнаты", "file": "049_Al_Nujraat.mp3", "description": ""},
    "50": {"name_ar": "Каф", "name_ru": "Каф", "file": "050_Qaf.mp3", "description": ""},
    "51": {"name_ar": "Аз-Зарият", "name_ru": "Рассеивающие", "file": "051_Ad_Dhariyat.mp3", "description": ""},
    "52": {"name_ar": "Ат-Тур", "name_ru": "Гора", "file": "052_At_Tur.mp3", "description": ""},
    "53": {"name_ar": "Ан-Наджм", "name_ru": "Звезда", "file": "053_An_Najm.mp3", "description": ""},
    "54": {"name_ar": "Аль-Камар", "name_ru": "Месяц", "file": "054_Al_Qamar.mp3", "description": ""},
    "55": {"name_ar": "Ар-Рахман", "name_ru": "Милосердный", "file": "055_Ar_Rahman.mp3", "description": ""},
    "56": {"name_ar": "Аль-Вакиа", "name_ru": "Падающее", "file": "056_Al_Waqia.mp3", "description": ""},
    "57": {"name_ar": "Аль-Хадид", "name_ru": "Железо", "file": "057_Al_Hadid.mp3", "description": ""},
    "58": {"name_ar": "Аль-Муджадила", "name_ru": "Препирательство", "file": "058_Al_Mujadala.mp3", "description": ""},
    "59": {"name_ar": "Аль-Хашр", "name_ru": "Собрание", "file": "059_Al_Hashr.mp3", "description": ""},
    "60": {"name_ar": "Аль-Мумтахана", "name_ru": "Испытуемая", "file": "060_Al_Mumtahana.mp3", "description": ""},
    "61": {"name_ar": "Ас-Сафф", "name_ru": "Ряды", "file": "061_As_Saff.mp3", "description": ""},
    "62": {"name_ar": "Аль-Джума", "name_ru": "Пятница", "file": "062_Al_Jumua.mp3", "description": ""},
    "63": {"name_ar": "Аль-Мунафикун", "name_ru": "Лицемеры", "file": "063_Al_Munafiqoon.mp3", "description": ""},
    "64": {"name_ar": "Ат-Тагабун", "name_ru": "Взаимное обманывание", "file": "064_At_Taghabun.mp3", "description": ""},
    "65": {"name_ar": "Ат-Талак", "name_ru": "Развод", "file": "065_At_Talaq.mp3", "description": ""},
    "66": {"name_ar": "Ат-Тахрим", "name_ru": "Запрещение", "file": "066_At_Tahrim.mp3", "description": ""},
    "67": {"name_ar": "Аль-Мульк", "name_ru": "Власть", "file": "067_Al_Mulk.mp3", "description": ""},
    "68": {"name_ar": "Аль-Калям", "name_ru": "Письменная трость", "file": "068_Al_Qalam.mp3", "description": ""},
    "69": {"name_ar": "Аль-Хакка", "name_ru": "Неизбежное", "file": "069_Al_Haqqa.mp3", "description": ""},
    "70": {"name_ar": "Аль-Мааридж", "name_ru": "Ступени", "file": "070_Al_Maarij.mp3", "description": ""},
    "71": {"name_ar": "Нух", "name_ru": "Нух", "file": "071_Nooh.mp3", "description": ""},
    "72": {"name_ar": "Аль-Джинн", "name_ru": "Джинны", "file": "072_Al_Jinn.mp3", "description": ""},
    "73": {"name_ar": "Аль-Муззаммиль", "name_ru": "Закутавшийся", "file": "073_Al_Muzzamill.mp3", "description": ""},
    "74": {"name_ar": "Аль-Муддассир", "name_ru": "Завернувшийся", "file": "074_Al_Muddaththir.mp3", "description": ""},
    "75": {"name_ar": "Аль-Кийама", "name_ru": "Воскресение", "file": "075_Al_Qiyama.mp3", "description": ""},
    "76": {"name_ar": "Аль-Инсан", "name_ru": "Человек", "file": "076_Al_Insan.mp3", "description": ""},
    "77": {"name_ar": "Аль-Мурсалят", "name_ru": "Посылаемые", "file": "077_Al_Mursalat.mp3", "description": ""},
    "78": {"name_ar": "Ан-Наба", "name_ru": "Весть", "file": "078_An_Naba.mp3", "description": ""},
    "79": {"name_ar": "Ан-Назиат", "name_ru": "Вырывающие", "file": "079_An_Naziat.mp3", "description": ""},
    "80": {"name_ar": "Абаса", "name_ru": "Нахмурился", "file": "080_Abasa.mp3", "description": ""},
    "81": {"name_ar": "Ат-Таквир", "name_ru": "Скручивание", "file": "081_Al_Takwir.mp3", "description": ""},
    "82": {"name_ar": "Аль-Инфитар", "name_ru": "Раскалывание", "file": "082_Al_Infitar.mp3", "description": ""},
    "83": {"name_ar": "Аль-Мутаффифин", "name_ru": "Обвешивающие", "file": "083_Al_Mutaffifin.mp3", "description": ""},
    "84": {"name_ar": "Аль-Иншикак", "name_ru": "Разверзнется", "file": "084_Al_Inshiqaq.mp3", "description": ""},
    "85": {"name_ar": "Аль-Бурудж", "name_ru": "Башни", "file": "085_Al_Burooj.mp3", "description": ""},
    "86": {"name_ar": "Ат-Тарик", "name_ru": "Ночной путник", "file": "086_At_Tariq.mp3", "description": ""},
    "87": {"name_ar": "Аль-Аля", "name_ru": "Высочайший", "file": "087_Al_Ala.mp3", "description": ""},
    "88": {"name_ar": "Аль-Гашия", "name_ru": "Покрывающее", "file": "088_Al_Ghashiya.mp3", "description": ""},
    "89": {"name_ar": "Аль-Фаджр", "name_ru": "Заря", "file": "089_Al_Fajr.mp3", "description": ""},
    "90": {"name_ar": "Аль-Балад", "name_ru": "Город", "file": "090_Al_Balad.mp3", "description": ""},
    "91": {"name_ar": "Аш-Шамс", "name_ru": "Солнце", "file": "091_Ash_Shams.mp3", "description": ""},
    "92": {"name_ar": "Аль-Лайл", "name_ru": "Ночь", "file": "092_Al_Layl.mp3", "description": ""},
    "93": {"name_ar": "Ад-Духа", "name_ru": "Утро", "file": "093_Ad_Dhuha.mp3", "description": ""},
    "94": {"name_ar": "Аш-Шарх", "name_ru": "Раскрытие", "file": "094_As_Sharh.mp3", "description": ""},
    "95": {"name_ar": "Ат-Тин", "name_ru": "Смоковница", "file": "095_At_Tin.mp3", "description": ""},
    "96": {"name_ar": "Аль-Алак", "name_ru": "Сгусток", "file": "096_Al_Alaq.mp3", "description": ""},
    "97": {"name_ar": "Аль-Кадр", "name_ru": "Могущество", "file": "097_Al_Qadr.mp3", "description": ""},
    "98": {"name_ar": "Аль-Баййина", "name_ru": "Ясное знамение", "file": "098_Al_Bayyina.mp3", "description": ""},
    "99": {"name_ar": "Аз-Залзала", "name_ru": "Землетрясение", "file": "099_Az_Zalzala.mp3", "description": ""},
    "100": {"name_ar": "Аль-Адият", "name_ru": "Скачущие", "file": "100_Al_Adiyat.mp3", "description": ""},
    "101": {"name_ar": "Аль-Кари'а", "name_ru": "Поражающее", "file": "101_Al_Qaria.mp3", "description": ""},
    "102": {"name_ar": "Ат-Такасур", "name_ru": "Приумножение", "file": "102_At_Takathur.mp3", "description": ""},
    "103": {"name_ar": "Аль-Аср", "name_ru": "Предвечернее время", "file": "103_Al_Asr.mp3", "description": ""},
    "104": {"name_ar": "Аль-Хумаза", "name_ru": "Хулитель", "file": "104_Al_Humaza.mp3", "description": ""},
    "105": {"name_ar": "Аль-Филь", "name_ru": "Слон", "file": "105_Al_Fil.mp3", "description": ""},
    "106": {"name_ar": "Курайш", "name_ru": "Курайшиты", "file": "106_Quraish.mp3", "description": ""},
    "107": {"name_ar": "Аль-Маун", "name_ru": "Милостыня", "file": "107_Al_Maun.mp3", "description": ""},
    "108": {"name_ar": "Аль-Каусар", "name_ru": "Изобилие", "file": "108_Al_Kauther.mp3", "description": ""},
    "109": {"name_ar": "Аль-Кафирун", "name_ru": "Неверующие", "file": "109_Al_Kafiroon.mp3", "description": ""},
    "110": {"name_ar": "Ан-Наср", "name_ru": "Помощь", "file": "110_An_Nasr.mp3", "description": ""},
    "111": {"name_ar": "Аль-Масад", "name_ru": "Пальмовые волокна", "file": "111_Al_Masadd.mp3", "description": ""},
    "112": {"name_ar": "Аль-Ихлас", "name_ru": "Очищение веры", "file": "112_Al_Ikhlas.mp3", "description": ""},
    "113": {"name_ar": "Аль-Фаляк", "name_ru": "Рассвет", "file": "113_Al_Falaq.mp3", "description": ""},
    "114": {"name_ar": "Ан-Нас", "name_ru": "Люди", "file": "114_An_Nas.mp3", "description": ""},
}

# Количество сур на странице
SURAS_PER_PAGE = 10


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


def get_suras_keyboard(page: int = 1) -> InlineKeyboardMarkup:
    """Создание клавиатуры с сурами для указанной страницы"""
    buttons = []
    start = (page - 1) * SURAS_PER_PAGE + 1
    end = min(start + SURAS_PER_PAGE - 1, len(SURAS))
    
    # Кнопки с сурами (по 2 в ряд)
    i = start
    while i <= end:
        row = []
        # Первая кнопка в ряду
        sura = SURAS[str(i)]
        button_text = f"{i}️⃣ {sura['name_ar']}"
        row.append(InlineKeyboardButton(text=button_text, callback_data=f"sura_{i}"))
        
        # Вторая кнопка в ряду (если есть)
        if i + 1 <= end:
            next_sura = SURAS[str(i + 1)]
            row.append(InlineKeyboardButton(
                text=f"{i + 1}️⃣ {next_sura['name_ar']}",
                callback_data=f"sura_{i + 1}"
            ))
            i += 2
        else:
            i += 1
        
        buttons.append(row)
    
    # Кнопки навигации
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"quran_page_{page - 1}"))
    total_pages = (len(SURAS) + SURAS_PER_PAGE - 1) // SURAS_PER_PAGE
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"quran_page_{page + 1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data == "quran_assaadi")
async def callback_quran_assaadi(callback: CallbackQuery):
    """Толкование Корана ас-Саади - первая страница"""
    keyboard = get_suras_keyboard(page=1)
    text = "📖 **Толкование Корана ас-Саади**\n\nВыберите суру:"
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("quran_page_"))
async def callback_quran_page(callback: CallbackQuery):
    """Переключение страниц с сурами"""
    page = int(callback.data.split("_")[-1])
    keyboard = get_suras_keyboard(page=page)
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
    
    # Формируем текст с описанием, если оно есть
    text = f"🎧 Сура {sura_num}\n«{sura['name_ar']}» — «{sura['name_ru']}»"
    if sura.get("description"):
        text += f"\n\n{sura['description']}"
    
    if audio_path.exists():
        try:
            # Показываем индикатор отправки
            await callback.message.delete()
            loading_message = await callback.message.answer("⏳ Идет отправка файла...")
            
            # Отправляем файл
            audio_file = FSInputFile(audio_path)
            await callback.message.answer_audio(
                audio=audio_file,
                title=f"Сура {sura_num}. {sura['name_ar']}",
                performer="Толкование ас-Саади",
                caption=text,
            )
            
            # Удаляем индикатор отправки
            await loading_message.delete()
            await callback.answer()
        except Exception as e:
            logger.error(f"Ошибка отправки аудиофайла {sura['file']}: {e}", exc_info=True)
            await callback.message.edit_text(
                f"{text}\n\n❌ Ошибка отправки файла. Файл слишком большой (максимум 50MB для Telegram).\n\nРазмер файла: {audio_path.stat().st_size / (1024*1024):.1f} MB",
            )
            await callback.answer("Ошибка отправки файла", show_alert=True)
    else:
        await callback.message.edit_text(
            f"{text}\n\n❌ Аудиофайл не найден: {audio_path}",
        )
        await callback.answer("Аудиофайл не найден", show_alert=True)


def register_quran_handlers(dp):
    """Регистрация обработчиков"""
    dp.include_router(router)