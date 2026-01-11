"""Сервис для работы с курсами"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional

from src.database.models import Course, Lesson, UserCourseProgress, UserSkill, Skill
from datetime import datetime


async def get_active_courses(session: AsyncSession) -> List[Course]:
    """Получить все активные курсы"""
    result = await session.execute(
        select(Course)
        .where(Course.is_active == True)
        .order_by(Course.sort_order, Course.id)
    )
    return list(result.scalars().all())


async def get_course(session: AsyncSession, course_id: int) -> Optional[Course]:
    """Получить курс по ID"""
    result = await session.execute(
        select(Course)
        .options(selectinload(Course.lessons))
        .where(Course.id == course_id)
    )
    return result.scalar_one_or_none()


async def get_lesson(session: AsyncSession, lesson_id: int) -> Optional[Lesson]:
    """Получить урок по ID"""
    result = await session.execute(
        select(Lesson).where(Lesson.id == lesson_id)
    )
    return result.scalar_one_or_none()


async def get_lesson_by_day(session: AsyncSession, course_id: int, day_number: int) -> Optional[Lesson]:
    """Получить урок по номеру дня курса"""
    result = await session.execute(
        select(Lesson)
        .where(and_(Lesson.course_id == course_id, Lesson.day_number == day_number))
    )
    return result.scalar_one_or_none()


async def start_course(
    session: AsyncSession,
    user_id: int,
    course_id: int,
) -> UserCourseProgress:
    """Начать курс"""
    # Проверяем, не начат ли уже курс
    result = await session.execute(
        select(UserCourseProgress).where(
            and_(
                UserCourseProgress.user_id == user_id,
                UserCourseProgress.course_id == course_id,
            )
        )
    )
    progress = result.scalar_one_or_none()
    
    if not progress:
        progress = UserCourseProgress(
            user_id=user_id,
            course_id=course_id,
            current_lesson_day=1,
            status="active",
        )
        session.add(progress)
        await session.commit()
        await session.refresh(progress)
    elif progress.status == "paused" or progress.status == "abandoned":
        progress.status = "active"
        progress.last_activity = datetime.now()
        await session.commit()
        await session.refresh(progress)
    
    return progress


async def get_user_course_progress(
    session: AsyncSession,
    user_id: int,
    course_id: int,
) -> Optional[UserCourseProgress]:
    """Получить прогресс пользователя по курсу"""
    result = await session.execute(
        select(UserCourseProgress).where(
            and_(
                UserCourseProgress.user_id == user_id,
                UserCourseProgress.course_id == course_id,
            )
        )
    )
    return result.scalar_one_or_none()


async def unlock_next_lesson(
    session: AsyncSession,
    user_id: int,
    course_id: int,
) -> bool:
    """Открыть следующий урок, если выполнены все навыки текущего дня"""
    progress = await get_user_course_progress(session, user_id, course_id)
    
    if not progress or progress.status != "active":
        return False
    
    current_day = progress.current_lesson_day
    
    # Получаем все навыки для текущего дня курса
    result = await session.execute(
        select(Skill).where(
            and_(
                Skill.course_id == course_id,
                Skill.lesson_day == current_day,
                Skill.is_active == True,
            )
        )
    )
    skills = list(result.scalars().all())
    
    if not skills:
        # Если навыков нет, просто открываем следующий урок
        course = await get_course(session, course_id)
        if course and current_day < course.total_days:
            progress.current_lesson_day += 1
            progress.last_activity = datetime.now()
            await session.commit()
            return True
        return False
    
    # Проверяем, выполнены ли все навыки
    all_completed = True
    for skill in skills:
        skill_progress_result = await session.execute(
            select(UserSkill).where(
                and_(
                    UserSkill.user_id == user_id,
                    UserSkill.skill_id == skill.id,
                )
            )
        )
        skill_progress = skill_progress_result.scalar_one_or_none()
        
        if not skill_progress or skill_progress.status != "completed":
            all_completed = False
            break
    
    if all_completed:
        course = await get_course(session, course_id)
        if course:
            if current_day < course.total_days:
                progress.current_lesson_day += 1
                progress.last_activity = datetime.now()
            else:
                # Курс завершен
                progress.status = "completed"
                progress.completed_at = datetime.now()
            
            await session.commit()
            return True
    
    return False