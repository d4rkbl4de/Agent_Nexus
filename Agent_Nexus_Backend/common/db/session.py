import contextlib
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from common.db.engine import AsyncSessionLocal
from common.config.logging import logger
from common.schemas.errors import AppError, ErrorCategory

@contextlib.asynccontextmanager
async def transactional_session() -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"TRANSACTION_ROLLBACK | Reason: {str(e)}")
        if isinstance(e, AppError):
            raise e
        raise AppError(
            message="Database transaction failed and was rolled back",
            category=ErrorCategory.INTERNAL_ERROR,
            status_code=500
        )
    finally:
        await session.close()

class SessionManager:
    @staticmethod
    async def get_session() -> AsyncGenerator[AsyncSession, None]:
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    @staticmethod
    async def execute_in_transaction(func, *args, **kwargs):
        async with transactional_session() as session:
            return await func(session, *args, **kwargs)

session_manager = SessionManager()