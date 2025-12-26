import asyncio
import time
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel, ValidationError
from common.config.logging import logger
from common.agent_sdk.orchestration_state import OrchestrationState
from common.agent_sdk.planner import PlanStep
from tracing.context import get_trace_id
from policy.execution_policy import execution_guard

class ExecutionResult(BaseModel):
    step_id: int
    success: bool
    output: Any
    execution_time_ms: float
    error: Optional[str] = None
    retry_count: int = 0

class Executor:
    def __init__(self):
        self._tools: Dict[str, Any] = {}

    def register_tool(self, name: str, tool_callable: Any):
        self._tools[name] = tool_callable

    @execution_guard(max_depth=5)
    async def execute(self, step: PlanStep, state: OrchestrationState) -> ExecutionResult:
        trace_id = get_trace_id()
        start_time = time.perf_counter()
        
        logger.info(f"EXECUTOR_ACTION_START | Trace: {trace_id} | Step: {step.step_id} | Action: