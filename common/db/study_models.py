from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class QuizAttemptModel(Base):
    __tablename__ = 'quiz_attempts'

    quiz_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    topic_key = Column(String)
    question = Column(String)
    user_answer = Column(String)
    correct_answer = Column(String)
    score = Column(Float)

class StudyPlanModel(Base):
    __tablename__ = 'study_plans'

    user_id = Column(String, primary_key=True)
    current_topic = Column(String)
    last_action = Column(String)
    next_instruction = Column(String)