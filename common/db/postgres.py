import json
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from common.config import settings
import uuid

class PostgresClient:
    _instance = None

    def __new__(cls, database_url: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.database_url = database_url or settings.DATABASE_URL
            cls._instance.engine = create_async_engine(
                cls._instance.database_url,
                pool_pre_ping=True,
                future=True
            )
            cls._instance.AsyncSessionLocal = sessionmaker(
                cls._instance.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
        return cls._instance

    @asynccontextmanager
    async def get_session(self):
        async with self.AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def save_quiz_attempt(self, attempt_data):
        from common.db.models import QuizAttemptModel
        async with self.get_session() as session:
            session.add(
                QuizAttemptModel(
                    quiz_id=attempt_data.quiz_id,
                    user_id=attempt_data.user_id,
                    topic_key=attempt_data.topic_key,
                    question=attempt_data.question,
                    user_answer=attempt_data.user_answer,
                    correct_answer=attempt_data.correct_answer,
                    score=attempt_data.score
                )
            )

    async def save_conversation_message(self, message_data):
        from common.db.models import ConversationMessageModel
        async with self.get_session() as session:
            session.add(
                ConversationMessageModel(
                    id=str(uuid.uuid4()),
                    user_id=message_data.user_id,
                    session_id=message_data.session_id,
                    message_type=message_data.message_type,
                    content=message_data.content,
                    timestamp=message_data.timestamp
                )
            )

    async def get_user_profile(self, user_id: str):
        from common.db.models import UserProfileSummaryModel
        async with self.get_session() as session:
            result = await session.execute(
                select(UserProfileSummaryModel).where(
                    UserProfileSummaryModel.user_id == user_id
                )
            )
            profile = result.scalars().first()