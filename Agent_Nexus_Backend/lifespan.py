import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from common.config.settings import settings
from common.db.engine import engine
from common.config.logging import logger
from health.checks import check_system_health
from resilience.circuit_breaker import CircuitBreaker

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.circuit_breaker = CircuitBreaker(
        failure_threshold=settings.CIRCUIT_FAILURE_THRESHOLD,
        recovery_timeout=settings.CIRCUIT_RECOVERY_TIMEOUT
    )
    
    try:
        health_status = await check_system_health()
        if not health_status["status"] == "healthy":
            logger.warning(f"System health degraded at startup: {health_status}")
    except Exception as e:
        logger.error(f"Critical failure during health check: {str(e)}")

    yield

    try:
        shutdown_tasks = [
            engine.dispose(),
        ]
        
        if hasattr(app.state, "redis_client"):
            shutdown_tasks.append(app.state.redis_client.close())
            
        await asyncio.gather(*shutdown_tasks, return_exceptions=True)
    except Exception as e:
        logger.error(f"Error during graceful shutdown: {str(e)}")
    finally:
        logger.info("Hive Mind Thalamus shutdown sequence complete.")