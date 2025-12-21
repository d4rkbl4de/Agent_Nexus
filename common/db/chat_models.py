from sqlalchemy import Column, String, Float, Text, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ConversationMessageModel(Base):
    __tablename__ = 'chat_messages'

    id = Column(String, primary_key=True)
    user_id = Column(String)
    session_id = Column(String)
    message_type = Column(String)
    content = Column(Text)
    timestamp = Column(Float)

class UserProfileSummaryModel(Base):
    __tablename__ = 'user_profiles'

    user_id = Column(String, primary_key=True)
    summary_id = Column(String, unique=True)
    name = Column(String)
    key_interests = Column(Text)
    key_facts = Column(Text)
    last_updated = Column(Float)