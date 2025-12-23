from sqlalchemy import Column, String, Float, BigInteger, Text, ForeignKey, DateTime, func
from common.db.base import Base
from common.db.mixins import AgenticTraceMixin

class StudyPlan(Base, AgenticTraceMixin):
    __tablename__ = 'study_plans'

    id = Column(String, primary_key=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    topic = Column(String(255), nullable=False)
    difficulty_level = Column(String(50), default="intermediate")
    
    plan_data = Column(Text, nullable=True)
    status = Column(String(50), default="active")

class Quiz(Base, AgenticTraceMixin):
    __tablename__ = 'quizzes'
    
    id = Column(String, primary_key=True)
    study_plan_id = Column(String, ForeignKey('study_plans.id'))
    topic_key = Column(String(100), index=True)
    content = Column(Text, nullable=False)

class QuizAttempt(Base, AgenticTraceMixin):
    __tablename__ = 'quiz_attempts'

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    quiz_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    
    score = Column(Float, nullable=False)
    user_responses = Column(Text, nullable=True)
    feedback_summary = Column(Text, nullable=True)
    
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())

class ProgressTracker(Base, AgenticTraceMixin):
    __tablename__ = 'progress_trackers'
    
    id = Column(BigInteger, primary_key=True)
    user_id = Column(String, ForeignKey('study_plans.user_id'), index=True)
    subject = Column(String(100))
    mastery_score = Column(Float, default=0.0)