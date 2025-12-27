import time
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from common.config.logging import logger

class ExecutionMetrics(BaseModel):
    trace_id: str
    agent_id: str
    lobe: str
    operation: str
    start_time: float = Field(default_factory=time.perf_counter)
    end_time: Optional[float] = None
    duration_ms: float = 0.0
    token_usage: Dict[str, int] = Field(default_factory=lambda: {"prompt": 0, "completion": 0, "total": 0})
    cost_usd: float = 0.0
    status: str = "PENDING"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MetricsRegistry:
    def __init__(self):
        self._active_metrics: Dict[str, ExecutionMetrics] = {}

    def start_segment(self, trace_id: str, agent_id: str, lobe: str, operation: str) -> str:
        metrics = ExecutionMetrics(
            trace_id=trace_id,
            agent_id=agent_id,
            lobe=lobe,
            operation=operation
        )
        self._active_metrics[trace_id] = metrics
        return trace_id

    def stop_segment(self, trace_id: str, status: str = "SUCCESS", tokens: Optional[Dict[str, int]] = None, cost: float = 0.0):
        if trace_id not in self._active_metrics:
            return

        metrics = self._active_metrics[trace_id]
        metrics.end_time = time.perf_counter()
        metrics.duration_ms = (metrics.end_time - metrics.start_time) * 1000
        metrics.status = status
        metrics.cost_usd = cost
        if tokens:
            metrics.token_usage.update(tokens)

        self._flush_to_logs(metrics)
        del self._active_metrics[trace_id]

    def _flush_to_logs(self, metrics: ExecutionMetrics):
        log_payload = {
            "event": "METRIC_SINK",
            "trace_id": metrics.trace_id,
            "agent_id": metrics.agent_id,
            "lobe": metrics.lobe,
            "op": metrics.operation,
            "duration": f"{metrics.duration_ms:.2f}ms",
            "tokens": metrics.token_usage["total"],
            "cost": f"${metrics.cost_usd:.6f}",
            "status": metrics.status
        }
        logger.info(json.dumps(log_payload))

metrics_registry = MetricsRegistry()