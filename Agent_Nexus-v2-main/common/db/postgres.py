import uuid
import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select
from contextlib import asynccontextmanager

class Base(DeclarativeBase):
    pass

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "agentnexus_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"

engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
    echo=False
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class PostgresClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.engine = engine
            cls._instance.session_factory = AsyncSessionLocal
        return cls._instance

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def save_quiz_attempt(self, attempt_data):
        from common.db.study_models import QuizAttempt
        async with self.get_session() as session:
            session.add(QuizAttempt(
                quiz_id=attempt_data.quiz_id,
                user_id=attempt_data.user_id,
                topic_key=attempt_data.topic_key,
                question=attempt_data.question,
                user_answer=attempt_data.user_answer,
                correct_answer=attempt_data.correct_answer,
                score=attempt_data.score
            ))

db_client = PostgresClient()

__all__ = ["Base", "engine", "AsyncSessionLocal", "db_client", "PostgresClient"]