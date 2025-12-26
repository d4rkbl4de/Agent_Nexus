import asyncio
import time
from typing import Dict, Any, List
from pydantic import BaseModel
from health.db import check_db_health
from health.redis import check_redis_health
from health.vector import check_vector_health
from health.llm import check_llm_health
from common.config.logging import logger

class HealthStatus(BaseModel):
    status: str
    timestamp: float
    version: str
    details: Dict[str, Any]
    latency_ms: Dict[str, float]

async def system_health_report() -> Dict[str, Any]:
    start_time = time.perf_counter()
    
    tasks = {
        "database": check_db_health(),
        "cache": check_redis_health(),
        "vector_db": check_vector_health(),
        "llm_provider": check_llm_health()
    }
    
    results = await asyncio.gather(*tasks.values(), return_exceptions=True)
    
    report = {}
    latencies = {}
    is_healthy = True
    
    for (key, task_func), result in zip(tasks.items(), results):
        task_start = time.perf_counter()
        if isinstance(result, Exception):
            logger.error(f"Health check failed for {key}: {str(result)}")
            report[key] = {"status": "unhealthy", "error": str(result)}
            is_healthy = False
        else:
            report[key] = result
            if result.get("status") != "healthy":
                is_healthy = False
        
        latencies[f"{key}_ms"] = round((time.perf_counter() - task_start) * 1000, 2)

    total_latency = round((time.perf_counter() - start_time) * 1000, 2)
    
    final_status = "healthy" if is_healthy else "degraded"
    if all(v.get("status") == "unhealthy" for v in report.values()):
        final_status = "unhealthy"

    return {
        "status": final_status,
        "timestamp": time.time(),
        "total_latency_ms": total_latency,
        "checks": report,
        "latencies": latencies
    }

async def check_system_health() -> Dict[str, Any]:
    try:
        return await system_health_report()
    except Exception as e:
        logger.critical(f"System health check orchestrator failure: {str(e)}")
        return {
            "status": "unhealthy",
            "error": "Orchestrator Failure",
            "timestamp": time.time()
        }