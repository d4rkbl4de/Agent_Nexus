import os
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from common.config.logging import logger

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/agent_nexus"
)

DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "1800"))

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_timeout=DB_POOL_TIMEOUT,
    pool_recycle=DB_POOL_RECYCLE,
    pool_pre_ping=True,
    echo=os.getenv("DB_ECHO", "False").lower() == "true",
    connect_args={
        "application_name": "agent_nexus_backend",
        "connect_timeout": 10,
        "options": "-c timezone=utc"
    }
)

logger.info(f"DB_ENGINE_INITIALIZED | Pool: {DB_POOL_SIZE} | Overflow: {DB_MAX_OVERFLOW}")