import time
from typing import Any, Dict, Optional
from common.config.logging import logger
from common.agent_sdk.base_agent import AgentMetadata
from tracing.context import get_trace_id

class AgentLifecycle:
    def __init__(self):
        self.start_time: Optional[float] = None

    async def on_bootstrap(self, metadata: AgentMetadata, trace_id: str) -> None:
        self.start_time = time.perf_counter()
        logger.info(
            f"LIFECYCLE_BOOTSTRAP | Agent: {metadata.agent_id} | "
            f"Version: {metadata.version} | Trace: {trace_id}"
        )

    async def on_success(self, metadata: AgentMetadata, result: Any) -> None:
        duration = (time.perf_counter() - self.start_time) * 1000 if self.start_time else 0
        logger.info(
            f"LIFECYCLE_SUCCESS | Agent: {metadata.agent_id} | "
            f"Duration: {duration:.2f}ms"
        )

    async def on_failure(self, metadata: AgentMetadata, error: Any) -> None:
        duration = (time.perf_counter() - self.start_time) * 1000 if self.start_time else 0
        logger.critical(
            f"LIFECYCLE_FAILURE | Agent: {metadata.agent_id} | "
            f"Duration: {duration:.2f}ms | Error_Type: {type(error).__name__}"
        )

    async def on_shutdown(self, metadata: AgentMetadata) -> None:
        logger.info(f"LIFECYCLE_SHUTDOWN | Agent: {metadata.agent_id}")