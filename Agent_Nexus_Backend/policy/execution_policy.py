import asyncio
import functools
import time
from typing import Dict, Any, Optional, Callable
 insurgent
from pydantic import BaseModel, Field
from common.config.logging import logger
from tracing.context import get_trace_id, get_agent_id

class ExecutionLimits(BaseModel):
    max_recursion_depth: int = Field(default=10, ge=1, le=50)
    max_execution_seconds: float = Field(default=60.0, gt=0)
    max_tool_calls: int = Field(default=5, ge=0)
    require_approval_for_tools: bool = False

class ExecutionPolicy:
    _depth_tracker: Dict[str, int] = {}
    _start_times: Dict[str, float] = {}
    _tool_call_tracker: Dict[str, int] = {}
    _lock = asyncio.Lock()

    def __init__(self, limits: Optional[ExecutionLimits] = None):
        self.limits = limits or ExecutionLimits()

    async def check_constraints(self, tool_use: bool = False) -> bool:
        trace_id = get_trace_id()
        if not trace_id:
            return True

        async with self._lock:
            if trace_id not in self._start_times:
                self._start_times[trace_id] = time.perf_counter()
                self._depth_tracker[trace_id] = 0
                self._tool_call_tracker[trace_id] = 0

            elapsed = time.perf_counter() - self._start_times[trace_id]
            if elapsed > self.limits.max_execution_seconds:
                logger.error(f"EXECUTION TIMEOUT: Trace {trace_id} exceeded {self.limits.max_execution_seconds}s")
                return False

            self._depth_tracker[trace_id] += 1
            if self._depth_tracker[trace_id] > self.limits.max_recursion_depth:
                logger.critical(f"RECURSION LIMIT: Trace {trace_id} hit max depth {self.limits.max_recursion_depth}")
                return False

            if tool_use:
                self._tool_call_tracker[trace_id] += 1
                if self._tool_call_tracker[trace_id] > self.limits.max_tool_calls:
                    logger.warning(f"TOOL LIMIT: Trace {trace_id} exceeded tool budget of {self.limits.max_tool_calls}")
                    return False

            return True

    async def cleanup(self):
        trace_id = get_trace_id()
        async with self._lock:
            self._start_times.pop(trace_id, None)
            self._depth_tracker.pop(trace_id, None)
            self._tool_call_tracker.pop(trace_id, None)

def execution_guard(max_depth: int = 10, max_tools: int = 5):
    def decorator(func: Callable):
        limits = ExecutionLimits(max_recursion_depth=max_depth, max_tool_calls=max_tools)
        policy = ExecutionPolicy(limits)

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            is_valid = await policy.check_constraints(tool_use="tool" in func.__name__.lower())
            
            if not is_valid:
                raise PermissionError(f"Execution Policy Violation on trace {get_trace_id()}")
            
            try:
                return await func(*args, **kwargs)
            finally:
                pass
        return wrapper
    return decorator