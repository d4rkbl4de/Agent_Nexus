import asyncio
import sys
from sqlalchemy import text
from src.core.db.engine import engine
from src.core.vector.qdrant_client import get_qdrant_client
from src.core.llm.provider import get_llm_provider

async def check_db():
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))

def check_vector():
    client = get_qdrant_client()
    client.get_collections()

async def check_llm():
    provider = get_llm_provider()
    await provider.ping()

async def main():
    try:
        await check_db()
        check_vector()
        await check_llm()
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
