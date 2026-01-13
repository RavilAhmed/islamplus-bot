"""Сервис для работы с уроками и тестами"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, Dict, List
from datetime import datetime

from src.database.models import (
    Lesson, UserLessonProgress, UserLessonQuiz, 
    UserCourseProgress, Skill, UserSkill
)


async def get_user_lesson_progress(
    session: AsyncSession,
    user_id: int,
    lesson_id: int,
) -> Optional[UserLessonProgress]:
    """Получить прогресс пользователя по уроку"""
    result = await session.execute(
        select(UserLessonProgress).where(
            and_(
                UserLessonProgress.user_id == user_id,
                UserLessonProgress.lesson_id == lesson_id,
            )
        )
    )
    return result.scalar_one_or_none()


async def mark_lesson_studied(
    session: AsyncSession,
    user_id: int,
    lesson_id: int,
) -> UserLessonProgress:
    """Отметить урок как изученный"""
    progress = await get_user_lesson_progress(session, user_id, lesson_id)
    
    if not progress:
        progress = UserLessonProgress(
            user_id=user_id,
            lesson_id=lesson_id,
            status="studied",
            started_at=datetime.now(),
            last_activity=datetime.now(),
        )
        session.add(progress)
    else:
        if progress.status == "not_started":
            progress.status = "studied"
            progress.started_at = datetime.now()
        progress.last_activity = datetime.now()
    
    await session.commit()
    await session.refresh(progress)
    return progress


async def get_lesson_quiz(
    session: AsyncSession,
    lesson_id: int,
) -> Optional[Dict]:
    """Получить вопросы теста для урока"""
    result = await session.execute(
        select(Lesson).where(Lesson.id == lesson_id)
    )
    lesson = result.scalar_one_or_none()
    
    if lesson and lesson.quiz_questions:
        return lesson.quiz_questions
    return None


async def submit_quiz_answer(
    session: AsyncSession,
    user_id: int,
    lesson_id: int,
    question_index: int,
    answer_index: int,
) -> Dict:
    """
    Отправить ответ на вопрос теста
    
    Returns:
        {
            "correct": bool,
            "score": int,  # процент правильных ответов
            "passed": bool,
            "explanation": str
        }
    """
    lesson = await session.get(Lesson, lesson_id)
    if not lesson or not lesson.quiz_questions:
        return {"error": "Тест не найден"}
    
    quiz_data = lesson.quiz_questions
    questions = quiz_data.get("questions", [])
    
    if question_index >= len(questions):
        return {"error": "Вопрос не найден"}
    
    question = questions[question_index]
    is_correct = question.get("correct") == answer_index
    
    # Получаем или создаем запись о тесте
    result = await session.execute(
        select(UserLessonQuiz).where(
            and_(
                UserLessonQuiz.user_id == user_id,
                UserLessonQuiz.lesson_id == lesson_id,
            )
        )
    )
    quiz_result = result.scalar_one_or_none()
    
    if not quiz_result:
        quiz_result = UserLessonQuiz(
            user_id=user_id,
            lesson_id=lesson_id,
            attempts=0,
            answers={},
        )
        session.add(quiz_result)
    
    # Сохраняем ответ
    if "answers" not in quiz_result.answers:
        quiz_result.answers = {}
    
    quiz_result.answers[str(question_index)] = {
        "answer": answer_index,
        "correct": is_correct,
        "timestamp": datetime.now().isoformat()
    }
    
    # Подсчитываем результат
    total_questions = len(questions)
    correct_answers = sum(
        1 for ans in quiz_result.answers.values() 
        if ans.get("correct", False)
    )
    
    if is_correct:
        correct_answers += 1
    
    score = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
    passed = score >= 70  # 70% для прохождения
    
    quiz_result.attempts += 1
    quiz_result.last_score = score
    quiz_result.passed = passed
    
    if passed:
        quiz_result.completed_at = datetime.now()
    
    await session.commit()
    await session.refresh(quiz_result)
    
    # Обновляем прогресс урока
    lesson_progress = await get_user_lesson_progress(session, user_id, lesson_id)
    if lesson_progress:
        if passed and lesson_progress.status == "studied":
            lesson_progress.status = "quiz_passed"
            lesson_progress.progress_data["quiz_passed"] = True
            lesson_progress.progress_data["quiz_score"] = score
            await session.commit()
    
    return {
        "correct": is_correct,
        "score": score,
        "passed": passed,
        "explanation": question.get("explanation", ""),
        "total_questions": total_questions,
        "correct_answers": correct_answers,
    }


async def check_lesson_completion(
    session: AsyncSession,
    user_id: int,
    lesson_id: int,
) -> bool:
    """
    Проверить, завершен ли урок (тест пройден + практика выполнена)
    
    Returns:
        True если урок полностью завершен
    """
    lesson = await session.get(Lesson, lesson_id)
    if not lesson:
        return False
    
    # Проверяем тест
    quiz_result = await session.execute(
        select(UserLessonQuiz).where(
            and_(
                UserLessonQuiz.user_id == user_id,
                UserLessonQuiz.lesson_id == lesson_id,
                UserLessonQuiz.passed == True,
            )
        )
    )
    quiz_passed = quiz_result.scalar_one_or_none() is not None
    
    if not quiz_passed:
        return False
    
    # Проверяем практические задания
    skills_result = await session.execute(
        select(Skill).where(
            and_(
                Skill.course_id == lesson.course_id,
                Skill.lesson_day == lesson.day_number,
                Skill.is_active == True,
            )
        )
    )
    skills = list(skills_result.scalars().all())
    
    if not skills:
        # Если практических заданий нет, урок завершен после теста
        lesson_progress = await get_user_lesson_progress(session, user_id, lesson_id)
        if lesson_progress and lesson_progress.status != "completed":
            lesson_progress.status = "completed"
            lesson_progress.completed_at = datetime.now()
            await session.commit()
        return True
    
    # Проверяем, выполнены ли все практические задания
    all_skills_completed = True
    for skill in skills:
        skill_progress_result = await session.execute(
            select(UserSkill).where(
                and_(
                    UserSkill.user_id == user_id,
                    UserSkill.skill_id == skill.id,
                    UserSkill.status == "completed",
                )
            )
        )
        if not skill_progress_result.scalar_one_or_none():
            all_skills_completed = False
            break
    
    if all_skills_completed:
        lesson_progress = await get_user_lesson_progress(session, user_id, lesson_id)
        if lesson_progress:
            lesson_progress.status = "completed"
            lesson_progress.completed_at = datetime.now()
            await session.commit()
    
    return all_skills_completed


async def unlock_next_lesson_after_completion(
    session: AsyncSession,
    user_id: int,
    course_id: int,
    completed_lesson_day: int,
) -> bool:
    """
    Разблокировать следующий урок после завершения текущего
    
    Returns:
        True если следующий урок разблокирован
    """
    progress = await session.execute(
        select(UserCourseProgress).where(
            and_(
                UserCourseProgress.user_id == user_id,
                UserCourseProgress.course_id == course_id,
            )
        )
    )
    course_progress = progress.scalar_one_or_none()
    
    if not course_progress or course_progress.status != "active":
        return False
    
    # Проверяем, что завершенный урок - текущий
    if course_progress.current_lesson_day != completed_lesson_day:
        return False
    
    # Получаем курс для проверки общего количества дней
    from src.services.course_service import get_course
    course = await get_course(session, course_id)
    
    if not course:
        return False
    
    # Переходим к следующему уроку
    if completed_lesson_day < course.total_days:
        course_progress.current_lesson_day += 1
        course_progress.last_activity = datetime.now()
        await session.commit()
        return True
    else:
        # Курс завершен
        course_progress.status = "completed"
        course_progress.completed_at = datetime.now()
        await session.commit()
        return False
