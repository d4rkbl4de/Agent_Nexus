from sqlalchemy import Column, Integer, String, DateTime, Float, func, BigInteger
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class QuizAttemptModel(Base):
    __tablename__ = 'quiz_attempts'

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    quiz_id = Column(String, index=True, nullable=False)
    user_id = Column(String, index=True, nullable=False)
    topic_key = Column(String, index=True, nullable=False)
    question = Column(String, nullable=False)
    user_answer = Column(String, nullable=False)
    correct_answer = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=func.now())

class ConversationMessageModel(Base):
    __tablename__ = 'conversation_messages'

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    session_id = Column(String, index=True, nullable=False)
    message_type = Column(String, nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now())

class UserProfileSummaryModel(Base):
    __tablename__ = 'user_profile_summaries'

    summary_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    key_interests = Column(String)
    key_facts = Column(String)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())