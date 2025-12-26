import asyncio
import time
from typing import Dict, Any
from common.data_sdk.vector_client import vector_client
from common.config.settings import settings
from common.config.logging import logger

async def check_vector_health() -> Dict[str, Any]:
    try:
        start_time = time.perf_counter()
        
.
        status = await vector_client.check_connectivity()
        
        latency = (time.perf_counter() - start_time) * 1000

        if not status["is_ready"]:
            return {
                "status": "unhealthy",
                "message": "Vector store reachable but collections are missing or corrupted",
                "latency_ms": round(latency, 2)
            }

        return {
            "status": "healthy",
            "latency_ms": round(latency, 2),
            "collection_count": status.get("collection_count", 0),
            "memory_mode": settings.VECTOR_DB_MODE
        }
    except Exception as e:

        logger.error(f"Vector DB (Semantic Memory) Health Check Failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(type(e).__name__),
            "message": "Vector Database (Semantic/Long-term Memory) is offline"
        }