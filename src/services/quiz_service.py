"""Сервис для работы с тестами"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional, Tuple
from datetime import datetime
import random

from src.database.models import QuizQuestion, UserQuizProgress, User
from src.services.user_service import add_points
from src.config import config


async def get_random_question(
    session: AsyncSession,
    category: Optional[str] = None,
) -> Optional[QuizQuestion]:
    """Получить случайный вопрос"""
    query = select(QuizQuestion).where(QuizQuestion.is_active == True)
    
    if category:
        query = query.where(QuizQuestion.category == category)
    
    result = await session.execute(query)
    questions = list(result.scalars().all())
    
    if not questions:
        return None
    
    return random.choice(questions)


async def get_question(session: AsyncSession, question_id: int) -> Optional[QuizQuestion]:
    """Получить вопрос по ID"""
    result = await session.execute(
        select(QuizQuestion).where(QuizQuestion.id == question_id)
    )
    return result.scalar_one_or_none()


async def get_user_quiz_progress(
    session: AsyncSession,
    user_id: int,
    quiz_mode: str,
) -> Optional[UserQuizProgress]:
    """Получить прогресс пользователя по тесту"""
    result = await session.execute(
        select(UserQuizProgress).where(
            and_(
                UserQuizProgress.user_id == user_id,
                UserQuizProgress.quiz_mode == quiz_mode,
            )
        )
    )
    return result.scalar_one_or_none()


async def create_or_get_quiz_progress(
    session: AsyncSession,
    user_id: int,
    quiz_mode: str,
) -> UserQuizProgress:
    """Создать или получить прогресс пользователя по тесту"""
    progress = await get_user_quiz_progress(session, user_id, quiz_mode)
    
    if not progress:
        progress = UserQuizProgress(
            user_id=user_id,
            quiz_mode=quiz_mode,
        )
        session.add(progress)
        await session.commit()
        await session.refresh(progress)
    
    return progress


class QuizAnswerResult:
    """Результат ответа на вопрос"""
    def __init__(
        self,
        correct: bool,
        points: int = 0,
        current_streak: int = 0,
        multiplier: float = 1.0,
    ):
        self.correct = correct
        self.points = points
        self.current_streak = current_streak
        self.multiplier = multiplier


async def answer_question(
    session: AsyncSession,
    user_id: int,
    question_id: int,
    answer_index: int,
    quiz_mode: str = "infinite",
) -> QuizAnswerResult:
    """Ответить на вопрос"""
    question = await get_question(session, question_id)
    
    if not question:
        return QuizAnswerResult(False)
    
    # Получаем или создаем прогресс
    progress = await create_or_get_quiz_progress(session, user_id, quiz_mode)
    
    is_correct = answer_index == question.correct_answer
    
    # Вычисляем множитель на основе серии
    multiplier = min(1.0 + (progress.current_streak * 0.1), config.MAX_STREAK_MULTIPLIER)
    
    if is_correct:
        points = int(10 * question.difficulty * multiplier)
        progress.current_streak += 1
        progress.total_correct += 1
        
        if progress.current_streak > progress.longest_streak:
            progress.longest_streak = progress.current_streak
    else:
        points = 0
        progress.current_streak = 0
    
    progress.total_answered += 1
    progress.score += points
    progress.last_played = datetime.now()
    
    # Обновляем статистику по категориям
    if question.category not in progress.category_stats:
        progress.category_stats[question.category] = {"total": 0, "correct": 0}
    
    progress.category_stats[question.category]["total"] += 1
    if is_correct:
        progress.category_stats[question.category]["correct"] += 1
    
    # Начисляем очки пользователю
    if points > 0:
        user_result = await session.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one()
        await add_points(session, user, points)
    
    await session.commit()
    await session.refresh(progress)
    
    return QuizAnswerResult(
        correct=is_correct,
        points=points,
        current_streak=progress.current_streak,
        multiplier=multiplier,
    )


async def get_categories(session: AsyncSession) -> List[str]:
    """Получить список категорий вопросов"""
    result = await session.execute(
        select(QuizQuestion.category)
        .where(QuizQuestion.is_active == True)
        .distinct()
    )
    return [row[0] for row in result.all()]