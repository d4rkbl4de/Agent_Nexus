import asyncio
from typing import Dict, Any
from common.config.settings import settings
from common.config.logging import logger
from common.db.postgres import db_manager
from common.data_sdk.vector_client import VectorClient
from common.llm.client import LLMClient
from common.memory.manager import MemoryManager

class WorkerContext:
    def __init__(self):
        self.db = None
        self.vector_store = None
        self.llm = None
        self.memory = None
        self.initialized = False

    async def initialize(self):
        if self.initialized:
            return
            
        logger.info("Initializing Worker Context: Connecting to Hive Mind Infrastructure")
        
        try:
            await db_manager.connect()
            self.db = db_manager
            
            self.vector_store = VectorClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY
            )
            
            self.llm = LLMClient(
                provider=settings.DEFAULT_LLM_PROVIDER,
                model=settings.DEFAULT_LLM_MODEL
            )
            
            self.memory = MemoryManager(
                db=self.db,
                vector_client=self.vector_store
            )
            
            self.initialized = True
            logger.info("Worker Bootstrap Complete: All SDKs linked.")
            
        except Exception as e:
            logger.critical(f"BOOTSTRAP FAILURE: Could not initialize worker resources: {str(e)}")
            raise SystemExit("Worker cannot start without infrastructure connectivity.")

    async def shutdown(self):
        if self.db:
            await self.db.disconnect()
        logger.info("Worker Context Shutdown: Resources released.")

_global_context = WorkerContext()

def bootstrap_worker() -> WorkerContext:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(_global_context.initialize())
    else:
        loop.run_until_complete(_global_context.initialize())
    return _global_context