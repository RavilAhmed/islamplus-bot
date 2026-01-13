"""Скрипт для загрузки курса из DOCX файла в базу данных"""
import asyncio
import logging
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import config
from src.database.base import async_session_maker, init_db
from src.database.models import Course, Lesson
from src.utils.docx_parser import parse_docx_to_lessons, parse_docx_simple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def load_course_from_docx(
    session: AsyncSession,
    docx_path: Path,
    course_title: str,
    course_description: str = "",
    icon: str = "📚",
    difficulty_level: int = 1
):
    """
    Загружает курс из DOCX файла в базу данных
    
    Args:
        session: Сессия БД
        docx_path: Путь к DOCX файлу
        course_title: Название курса
        course_description: Описание курса
        icon: Иконка курса (эмодзи)
        difficulty_level: Уровень сложности (1-5)
    """
    try:
        # Проверяем существование файла
        if not docx_path.exists():
            raise FileNotFoundError(f"Файл не найден: {docx_path}")
        
        # Парсим DOCX
        logger.info(f"Парсинг файла: {docx_path}")
        try:
            lessons_data = parse_docx_to_lessons(docx_path)
        except Exception as e:
            logger.warning(f"Ошибка основного парсера, пробую простой: {e}")
            lessons_data = parse_docx_simple(docx_path)
        
        if not lessons_data:
            raise ValueError("Не удалось извлечь уроки из файла")
        
        logger.info(f"Извлечено {len(lessons_data)} уроков")
        
        # Создаем курс
        course = Course(
            title=course_title,
            description=course_description,
            icon=icon,
            difficulty_level=difficulty_level,
            total_days=len(lessons_data),
            is_active=True,
            sort_order=1
        )
        session.add(course)
        await session.flush()  # Получаем ID курса
        
        logger.info(f"Создан курс: {course.title} (ID: {course.id})")
        
        # Создаем уроки
        for lesson_data in lessons_data:
            lesson = Lesson(
                course_id=course.id,
                day_number=lesson_data["day_number"],
                title=lesson_data["title"],
                content_type="text",
                text_content=lesson_data["content"],
                quiz_questions=None,  # Тесты можно добавить позже
                additional_materials={},
                lesson_config={}
            )
            session.add(lesson)
            logger.info(f"  - Урок {lesson_data['day_number']}: {lesson_data['title']}")
        
        await session.commit()
        logger.info(f"✅ Курс '{course_title}' успешно загружен! Создано {len(lessons_data)} уроков")
        
        return course
        
    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка загрузки курса: {e}", exc_info=True)
        raise


async def main():
    """Главная функция"""
    # Инициализация БД
    await init_db()
    
    # Путь к файлу курса
    base_dir = Path(__file__).parent
    docx_path = base_dir / "kursi" / "roditeli.docx"
    
    # Параметры курса
    course_title = "Почтительность к родителям"
    course_description = (
        "Курс о важности почтительного отношения к родителям в исламе. "
        "Изучите аяты Корана, хадисы и практические советы по улучшению отношений с родителями."
    )
    
    async with async_session_maker() as session:
        try:
            course = await load_course_from_docx(
                session=session,
                docx_path=docx_path,
                course_title=course_title,
                course_description=course_description,
                icon="👨‍👩‍👧‍👦",
                difficulty_level=1
            )
            print(f"\n✅ Курс успешно загружен!")
            print(f"   Название: {course.title}")
            print(f"   Уроков: {course.total_days}")
            print(f"   ID курса: {course.id}")
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
