import asyncio
from typing import Dict, Any
from sqlalchemy import text
from common.db.engine import engine
from common.config.logging import logger

async def check_db_health() -> Dict[str, Any]:
    try:
        async with engine.connect() as conn:
            start_time = asyncio.get_event_loop().time()
            result = await conn.execute(text("SELECT 1"))
            await conn.commit()
            latency = (asyncio.get_event_loop().time() - start_time) * 1000

            pool_status = engine.pool.status()
            
            return {
                "status": "healthy",
                "latency_ms": round(latency, 2),
                "pool": {
                    "size": engine.pool.size(),
                    "checked_in": engine.pool.checkedin(),
                    "checked_out": engine.pool.checkedout(),
                    "overflow": engine.pool.overflow()
                }
            }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(type(e).__name__),
            "message": str(e)
        }