"""Модели базы данных"""
from sqlalchemy import (
    BigInteger,
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    DateTime,
    Date,
    JSON,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime, date
from typing import Optional, Dict, List

from .base import Base


class User(Base):
    """Пользователи"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    language_code: Mapped[str] = mapped_column(String(10), default="ru")
    points: Mapped[int] = mapped_column(Integer, default=0)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)  # дней подряд активности
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    settings: Mapped[Dict] = mapped_column(JSON, default=lambda: {"notifications": True, "daily_reminder": "20:00"})
    
    # Relationships
    course_progress: Mapped[List["UserCourseProgress"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    user_skills: Mapped[List["UserSkill"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    daily_focus: Mapped[List["DailyFocus"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    quiz_progress: Mapped[List["UserQuizProgress"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    achievements: Mapped[List["UserAchievement"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Course(Base):
    """Курсы"""
    __tablename__ = "courses"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    icon: Mapped[Optional[str]] = mapped_column(String(50))  # эмодзи
    difficulty_level: Mapped[int] = mapped_column(Integer, default=1)  # 1-5
    total_days: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    lessons: Mapped[List["Lesson"]] = relationship(back_populates="course", cascade="all, delete-orphan")
    skills: Mapped[List["Skill"]] = relationship(back_populates="course", cascade="all, delete-orphan")
    progress: Mapped[List["UserCourseProgress"]] = relationship(back_populates="course", cascade="all, delete-orphan")


class Lesson(Base):
    """Уроки в курсах"""
    __tablename__ = "lessons"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    course_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    day_number: Mapped[int] = mapped_column(Integer, nullable=False)  # день курса (1, 2, 3...)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'video', 'audio', 'text', 'mixed'
    content_url: Mapped[Optional[str]] = mapped_column(Text)  # ссылка на видео/аудио
    text_content: Mapped[Optional[str]] = mapped_column(Text)  # текст урока
    pdf_url: Mapped[Optional[str]] = mapped_column(Text)  # ссылка на PDF
    quiz_questions: Mapped[Optional[Dict]] = mapped_column(JSON)  # вопросы для проверки
    unlock_condition: Mapped[str] = mapped_column(String(50), default="previous_completed")
    
    # Relationships
    course: Mapped["Course"] = relationship(back_populates="lessons")
    
    __table_args__ = (
        Index("idx_lesson_course_day", "course_id", "day_number"),
    )


class Skill(Base):
    """Навыки (практические задания)"""
    __tablename__ = "skills"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    skill_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'course_skill', 'independent_habit'
    repetition_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'single', 'sequential', 'habit'
    target_streak: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_days: Mapped[Optional[int]] = mapped_column(Integer)  # для sequential
    points_per_completion: Mapped[int] = mapped_column(Integer, default=10)
    course_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("courses.id", ondelete="CASCADE"))
    lesson_day: Mapped[Optional[int]] = mapped_column(Integer)  # день курса, к которому привязан
    cooldown_hours: Mapped[int] = mapped_column(Integer, default=24)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Relationships
    course: Mapped[Optional["Course"]] = relationship(back_populates="skills")
    user_skills: Mapped[List["UserSkill"]] = relationship(back_populates="skill", cascade="all, delete-orphan")


class UserCourseProgress(Base):
    """Прогресс пользователя по курсам"""
    __tablename__ = "user_course_progress"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    current_lesson_day: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(50), default="active")  # 'active', 'paused', 'completed', 'abandoned'
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="course_progress")
    course: Mapped["Course"] = relationship(back_populates="progress")
    
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_user_course"),
        Index("idx_user_course", "user_id", "course_id"),
    )


class UserSkill(Base):
    """Прогресс пользователя по навыкам"""
    __tablename__ = "user_skills"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active")  # 'active', 'paused', 'completed', 'in_focus'
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    target_streak: Mapped[int] = mapped_column(Integer, nullable=False)
    last_completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    start_date: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    in_focus_today: Mapped[bool] = mapped_column(Boolean, default=False)
    focus_dates: Mapped[List] = mapped_column(JSON, default=lambda: [])  # даты, когда был в фокусе
    completed_dates: Mapped[List] = mapped_column(JSON, default=lambda: [])  # даты выполнения
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="user_skills")
    skill: Mapped["Skill"] = relationship(back_populates="user_skills")
    
    __table_args__ = (
        UniqueConstraint("user_id", "skill_id", name="uq_user_skill"),
        Index("idx_user_skill", "user_id", "skill_id"),
    )


class DailyFocus(Base):
    """Ежедневный фокус пользователя"""
    __tablename__ = "daily_focus"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[date] = mapped_column(Date, server_default=func.current_date(), nullable=False)
    skill_ids: Mapped[List] = mapped_column(JSON, default=lambda: [], nullable=False)
    completed_skill_ids: Mapped[List] = mapped_column(JSON, default=lambda: [])
    is_daily_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="daily_focus")
    
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_user_date"),
        Index("idx_user_date", "user_id", "date"),
    )


class QuizQuestion(Base):
    """Вопросы для Большого Теста"""
    __tablename__ = "quiz_questions"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(50), default="multiple_choice")  # 'multiple_choice', 'true_false'
    options: Mapped[List] = mapped_column(JSON, nullable=False)  # массив вариантов
    correct_answer: Mapped[int] = mapped_column(Integer, nullable=False)  # индекс правильного ответа (0-based)
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # 'aqeedah', 'fiqh', 'sira', 'quran', 'ethics'
    difficulty: Mapped[int] = mapped_column(Integer, default=1)  # 1-3
    explanation: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    __table_args__ = (
        Index("idx_quiz_category", "category"),
        Index("idx_quiz_active", "is_active"),
    )


class UserQuizProgress(Base):
    """Прогресс в тестах"""
    __tablename__ = "user_quiz_progress"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    quiz_mode: Mapped[str] = mapped_column(String(50), nullable=False)  # 'infinite', 'category', 'daily'
    score: Mapped[int] = mapped_column(Integer, default=0)
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    total_answered: Mapped[int] = mapped_column(Integer, default=0)
    total_correct: Mapped[int] = mapped_column(Integer, default=0)
    last_played: Mapped[Optional[datetime]] = mapped_column(DateTime)
    category_stats: Mapped[Dict] = mapped_column(JSON, default=lambda: {})
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="quiz_progress")
    
    __table_args__ = (
        UniqueConstraint("user_id", "quiz_mode", name="uq_user_quiz_mode"),
        Index("idx_user_quiz_mode", "user_id", "quiz_mode"),
    )


class Achievement(Base):
    """Достижения (бейджи)"""
    __tablename__ = "achievements"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    icon: Mapped[Optional[str]] = mapped_column(String(50))
    criteria_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'total_points', 'streak_days', 'courses_completed', 'skills_completed'
    criteria_value: Mapped[int] = mapped_column(Integer, nullable=False)
    points_reward: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    user_achievements: Mapped[List["UserAchievement"]] = relationship(back_populates="achievement", cascade="all, delete-orphan")


class UserAchievement(Base):
    """Достижения пользователей"""
    __tablename__ = "user_achievements"
    
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    achievement_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("achievements.id", ondelete="CASCADE"), primary_key=True)
    unlocked_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="achievements")
    achievement: Mapped["Achievement"] = relationship(back_populates="user_achievements")