"""Сервис для работы с навыками"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime, date, timedelta

from src.database.models import Skill, UserSkill, DailyFocus, User
from src.services.user_service import add_points
from src.services.course_service import unlock_next_lesson
from src.config import config


async def get_user_skill(
    session: AsyncSession,
    user_id: int,
    skill_id: int,
) -> Optional[UserSkill]:
    """Получить прогресс пользователя по навыку"""
    result = await session.execute(
        select(UserSkill).where(
            and_(
                UserSkill.user_id == user_id,
                UserSkill.skill_id == skill_id,
            )
        )
    )
    return result.scalar_one_or_none()


async def create_user_skill(
    session: AsyncSession,
    user_id: int,
    skill_id: int,
) -> UserSkill:
    """Создать прогресс пользователя по навыку"""
    skill_result = await session.execute(select(Skill).where(Skill.id == skill_id))
    skill = skill_result.scalar_one()
    
    user_skill = UserSkill(
        user_id=user_id,
        skill_id=skill_id,
        target_streak=skill.target_streak,
        status="active",
        start_date=date.today(),
    )
    
    if skill.repetition_type == "sequential" and skill.duration_days:
        user_skill.end_date = date.today() + timedelta(days=skill.duration_days)
    
    session.add(user_skill)
    await session.commit()
    await session.refresh(user_skill)
    return user_skill


class SkillCompletionResult:
    """Результат выполнения навыка"""
    def __init__(self, success: bool, points: int = 0, message: str = "", completed: bool = False):
        self.success = success
        self.points = points
        self.message = message
        self.completed = completed


async def complete_skill(
    session: AsyncSession,
    user_id: int,
    skill_id: int,
) -> SkillCompletionResult:
    """Выполнить навык"""
    # Получаем навык и прогресс пользователя
    skill_result = await session.execute(select(Skill).where(Skill.id == skill_id))
    skill = skill_result.scalar_one_or_none()
    
    if not skill or not skill.is_active:
        return SkillCompletionResult(False, message="Навык не найден")
    
    user_skill = await get_user_skill(session, user_id, skill_id)
    
    if not user_skill:
        user_skill = await create_user_skill(session, user_id, skill_id)
    
    if user_skill.status == "completed":
        return SkillCompletionResult(False, message="Навык уже завершен")
    
    # Проверка cooldown
    if user_skill.last_completed_at:
        time_since = datetime.now() - user_skill.last_completed_at
        cooldown = timedelta(hours=skill.cooldown_hours)
        
        if time_since < cooldown:
            hours_left = (cooldown - time_since).seconds // 3600
            return SkillCompletionResult(
                False,
                message=f"Вы уже выполняли это задание сегодня. Попробуйте через {hours_left} часов",
            )
    
    # Проверяем, в фокусе ли навык сегодня
    today_focus = await get_daily_focus(session, user_id, date.today())
    in_focus = (
        today_focus
        and skill_id in today_focus.skill_ids
    )
    
    # Начисляем очки
    points = skill.points_per_completion
    if in_focus:
        points = int(points * config.POINTS_MULTIPLIER_FOCUS)
    
    # Обновляем прогресс
    user_skill.current_streak += 1
    user_skill.last_completed_at = datetime.now()
    
    if date.today().isoformat() not in user_skill.completed_dates:
        user_skill.completed_dates.append(date.today().isoformat())
    
    # Проверяем завершение
    completed = False
    if user_skill.current_streak >= user_skill.target_streak:
        user_skill.status = "completed"
        completed = True
    
    # Начисляем очки пользователю
    user_result = await session.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one()
    await add_points(session, user, points)
    
    await session.commit()
    await session.refresh(user_skill)
    
    # Если навык привязан к курсу, проверяем открытие следующего урока
    if skill.course_id:
        await unlock_next_lesson(session, user_id, skill.course_id)
    
    return SkillCompletionResult(True, points=points, completed=completed)


async def get_daily_focus(
    session: AsyncSession,
    user_id: int,
    focus_date: date,
) -> Optional[DailyFocus]:
    """Получить ежедневный фокус пользователя"""
    result = await session.execute(
        select(DailyFocus).where(
            and_(
                DailyFocus.user_id == user_id,
                DailyFocus.date == focus_date,
            )
        )
    )
    return result.scalar_one_or_none()


async def set_daily_focus(
    session: AsyncSession,
    user_id: int,
    skill_ids: List[int],
) -> DailyFocus:
    """Установить ежедневный фокус пользователя"""
    if len(skill_ids) > config.DAILY_FOCUS_LIMIT:
        raise ValueError(f"Максимум {config.DAILY_FOCUS_LIMIT} навыков в фокусе")
    
    today = date.today()
    focus = await get_daily_focus(session, user_id, today)
    
    if not focus:
        focus = DailyFocus(
            user_id=user_id,
            date=today,
            skill_ids=skill_ids,
        )
        session.add(focus)
    else:
        focus.skill_ids = skill_ids
    
    # Обновляем in_focus_today для всех навыков пользователя
    all_user_skills_result = await session.execute(
        select(UserSkill).where(UserSkill.user_id == user_id)
    )
    all_user_skills = all_user_skills_result.scalars().all()
    
    for user_skill in all_user_skills:
        user_skill.in_focus_today = user_skill.skill_id in skill_ids
        if user_skill.skill_id in skill_ids:
            if today.isoformat() not in user_skill.focus_dates:
                user_skill.focus_dates.append(today.isoformat())
    
    await session.commit()
    await session.refresh(focus)
    return focus


async def get_active_user_skills(
    session: AsyncSession,
    user_id: int,
) -> List[UserSkill]:
    """Получить активные навыки пользователя"""
    result = await session.execute(
        select(UserSkill)
        .options(selectinload(UserSkill.skill))
        .where(
            and_(
                UserSkill.user_id == user_id,
                UserSkill.status.in_(["active", "in_focus"]),
            )
        )
        .order_by(UserSkill.start_date.desc())
    )
    return list(result.scalars().all())


from sqlalchemy.orm import selectinload