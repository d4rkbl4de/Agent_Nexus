import ssl
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from common.config.secrets import secrets
from common.config.logging import logger

DATABASE_URL = secrets.DATABASE_URL
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    connect_args={
        "command_timeout": 60,
        "server_settings": {
            "application_name": "agent_nexus_backend",
            "timezone": "UTC",
        }
    }
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"DATABASE_SESSION_ERROR | Error: {str(e)}")
            raise
        finally:
            await session.close()

async def init_db_connection() -> None:
    try:
        async with engine.begin() as conn:
            await conn.run_sync(lambda x: None)
        logger.info("DATABASE_ENGINE_READY | Connection pool initialized")
    except Exception as e:
        logger.critical(f"DATABASE_CONNECTION_FAILURE | Error: {str(e)}")
        raise

async def close_db_connection() -> None:
    await engine.dispose()
    logger.info("DATABASE_ENGINE_SHUTDOWN | Connection pool disposed")