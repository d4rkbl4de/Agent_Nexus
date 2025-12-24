import asyncio
import subprocess
import sys
from sqlalchemy import text
from src.core.db.engine import engine
from src.core.config.settings import settings

async def check_connection():
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))

def run_migrations():
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    if result.returncode != 0:
        sys.exit(1)

async def main():
    await check_connection()
    run_migrations()

if __name__ == "__main__":
    asyncio.run(main())
