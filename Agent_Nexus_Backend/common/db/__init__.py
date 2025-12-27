from common.db.base import Base, AgenticEntity, SingletonEntity
from common.db.engine import engine, get_db_session, init_db_connection, close_db_connection
from common.db.session import AsyncSessionLocal

class DatabaseManifest:
    def __init__(self):
        self.base = Base
        self.engine = engine
        self.session_factory = AsyncSessionLocal

    async def check_health(self) -> bool:
        try:
            async with self.engine.connect() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception:
            return False

db_manifest = DatabaseManifest()

__all__ = [
    "Base",
    "AgenticEntity",
    "SingletonEntity",
    "engine",
    "get_db_session",
    "init_db_connection",
    "close_db_connection",
    "AsyncSessionLocal",
    "db_manifest"
]