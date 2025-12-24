import logging
from functools import wraps
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from common.config import settings
from .postgres import AsyncSessionLocal
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Dependency for getting async database sessions."""
    session: AsyncSession = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception as e:
        logger.error(f"📡 Database session error: {e}")
        await session.rollback()
        raise
    finally:
        await session.close()

@asynccontextmanager
async def transactional_session() -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"❌ Transaction failed, rolling back: {e}")
        raise
    finally:
        await session.close()