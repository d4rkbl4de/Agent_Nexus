import asyncio
import time
from typing import Dict, Any
from common.ai_sdk.client import ai_client
from common.config.settings import settings
from common.config.logging import logger

async def check_llm_health() -> Dict[str, Any]:
    try:
        start_time = time.perf_counter()
        
        # Rule 13: Cost/Usage tracking is implicit in the client.health_check call
        # Rule 2: Agent SDK handles the infra communication
        status = await ai_client.perform_provider_health_check()
        
        latency = (time.perf_counter() - start_time) * 1000
        
        if latency > settings.LLM_LATENCY_THRESHOLD_MS:
            return {
                "status": "degraded",
                "message": "High latency detected from LLM provider",
                "latency_ms": round(latency, 2),
                "provider": settings.PRIMARY_LLM_PROVIDER
            }

        return {
            "status": "healthy",
            "latency_ms": round(latency, 2),
            "provider": settings.PRIMARY_LLM_PROVIDER,
            "available_models": status.get("models", [])
        }
    except Exception as e:
        # Rule 14: Explicitly log failure for escalation policies
        logger.error(f"LLM Provider Health Check Critical Failure: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(type(e).__name__),
            "message": "LLM Provider unreachable or API quota exhausted"
        }