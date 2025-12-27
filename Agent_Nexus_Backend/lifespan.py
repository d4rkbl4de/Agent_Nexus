import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI

from common.config.logging_config import logger
from common.memory.vector_db import vector_db_client
from common.memory.short_term import stm_client
from lobes import lobe_registry

@asynccontextmanager
async def lifespan(app: FastAPI):
    trace_id = "SYSTEM_BOOT_INIT"
    
    try:
        logger.info("BOOTSTRAP_START | Initializing Hive Mind Infrastructure", trace_id=trace_id)
        
        await stm_client.connect()
        logger.info("INFRA_READY | Short-Term Memory (Redis) Connected", trace_id=trace_id)
        
        await vector_db_client.connect()
        logger.info("INFRA_READY | Vector Database (Chroma/Qdrant) Connected", trace_id=trace_id)
        
        await lobe_registry.initialize_all()
        logger.info(f"LOBES_READY | Active Lobes: {', '.join(lobe_registry.list_active_lobes())}", trace_id=trace_id)
        
        logger.info("BOOTSTRAP_COMPLETE | Agent Nexus Backend is Online", trace_id=trace_id)
        yield
        
    except Exception as e:
        logger.critical(f"BOOTSTRAP_PANIC | System Failure during startup: {str(e)}", trace_id=trace_id)
        raise e
    
    finally:
        logger.info("SHUTDOWN_START | Commencing Graceful Teardown", trace_id=trace_id)
        
        shutdown_tasks = [
            stm_client.disconnect(),
            vector_db_client.disconnect()
        ]
        
        active_lobes = lobe_registry.list_active_lobes()
        for lobe_name in active_lobes:
            lobe = lobe_registry.get_lobe(lobe_name)
            if hasattr(lobe, "stop"):
                shutdown_tasks.append(lobe.stop())

        await asyncio.gather(*shutdown_tasks, return_exceptions=True)
        logger.info("SHUTDOWN_COMPLETE | All resources released", trace_id=trace_id)