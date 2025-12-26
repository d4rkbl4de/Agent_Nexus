import asyncio
import time
from typing import Dict, Any
from redis.asyncio import Redis
from common.config.settings import settings
from common.config.logging import logger

async def check_redis_health() -> Dict[str, Any]:
    try:
        start_time = time.perf_counter()
        
        # Rule 2: SDK/Client level abstraction for infrastructure
        client: Redis = Redis.from_url(
            settings.REDIS_URL, 
            encoding="utf-8", 
            decode_responses=True,
            socket_timeout=2.0
        )
        
        async with client:
            ping_success = await client.ping()
            if not ping_success:
                raise ConnectionError("Redis PING failed")
                
            info = await client.info(section="memory")
            latency = (time.perf_counter() - start_time) * 1000

            return {
                "status": "healthy",
                "latency_ms": round(latency, 2),
                "memory_usage": info.get("used_memory_human"),
                "peak_memory": info.get("used_memory_peak_human"),
                "fragmentation_ratio": info.get("mem_fragmentation_ratio")
            }
            
    except Exception as e:
        # Rule 14: Explicit escalation logging
        logger.error(f"Redis Health Check Failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(type(e).__name__),
            "message": "Redis/TaskQueue heartbeat lost"
        }