import asyncio
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from common.config.logging import logger
from tracing.context import get_trace_id, get_agent_id

class CostThresholds(BaseModel):
    max_tokens_per_trace: int = Field(default=100000, gt=0)
    max_usd_per_trace: float = Field(default=1.00, gt=0.0)
    hard_stop_usd: float = Field(default=5.00, gt=0.0)

class CostPolicy:
    _trace_costs: Dict[str, Dict[str, Any]] = {}
    _lock = asyncio.Lock()

    def __init__(self, thresholds: Optional[CostThresholds] = None):
        self.thresholds = thresholds or CostThresholds()

    async def track_and_validate(self, tokens: int, estimated_usd: float) -> bool:
        trace_id = get_trace_id()
        if not trace_id:
            return True

        async with self._lock:
            if trace_id not in self._trace_costs:
                self._trace_costs[trace_id] = {"tokens": 0, "usd": 0.0}

            self._trace_costs[trace_id]["tokens"] += tokens
            self._trace_costs[trace_id]["usd"] += estimated_usd

            current = self._trace_costs[trace_id]
            
            if current["usd"] >= self.thresholds.hard_stop_usd:
                logger.critical(
                    f"COST POLICY VIOLATION: Hard stop reached. Rule 13 Escalation. "
                    f"TraceID: {trace_id} | Total USD: {current['usd']}"
                )
                return False

            if current["usd"] >= self.thresholds.max_usd_per_trace:
                logger.warning(
                    f"Budget alert for trace {trace_id}. "
                    f"Current: ${current['usd']:.4f} | Limit: ${self.thresholds.max_usd_per_trace:.4f}"
                )
            
            return True

    async def get_current_trace_cost(self) -> Dict[str, Any]:
        trace_id = get_trace_id()
        return self._trace_costs.get(trace_id, {"tokens": 0, "usd": 0.0})

def budget_check(estimated_tokens: int = 1000):
    def decorator(func):
        policy = CostPolicy()
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Pre-execution sanity check
            current = await policy.get_current_trace_cost()
            if current["usd"] > policy.thresholds.max_usd_per_trace:
                raise PermissionError(f"Trace {get_trace_id()} has exceeded its budget.")
            
            result = await func(*args, **kwargs)
            
            # Post-execution update (assuming result returns usage metadata)
            if isinstance(result, dict) and "usage" in result:
                usage = result["usage"]
                await policy.track_and_validate(
                    tokens=usage.get("total_tokens", 0),
                    estimated_usd=usage.get("total_cost", 0.0)
                )
            return result
        return wrapper
    return decorator