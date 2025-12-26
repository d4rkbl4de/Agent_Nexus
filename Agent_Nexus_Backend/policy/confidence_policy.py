import asyncio
from typing import Any, Dict, Optional, Callable
from pydantic import BaseModel, Field
from common.config.logging import logger
from tracing.context import get_trace_id, get_agent_id

class ConfidenceThresholds(BaseModel):
    minimum_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    human_intervention_required: float = Field(default=0.4, ge=0.0, le=1.0)
    auto_retry_threshold: float = Field(default=0.6, ge=0.0, le=1.0)

class ConfidencePolicy:
    def __init__(self, thresholds: Optional[ConfidenceThresholds] = None):
        self.thresholds = thresholds or ConfidenceThresholds()

    async def validate_result(
        self, 
        confidence_score: float, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        trace_id = get_trace_id()
        agent_id = get_agent_id()
        
        if confidence_score < self.thresholds.human_intervention_required:
            logger.critical(
                f"Confidence CRITICAL failure. Rule 14 Escalation. "
                f"Score: {confidence_score} | TraceID: {trace_id} | Agent: {agent_id}"
            )
            return False

        if confidence_score < self.thresholds.minimum_threshold:
            logger.warning(
                f"Confidence below minimum threshold. Score: {confidence_score} | "
                f"TraceID: {trace_id} | Metadata: {metadata}"
            )
            return False

        return True

def validate_confidence(threshold: float = 0.7):
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # Logic assumes agent output contains a 'confidence' key
            score = result.get("confidence", 1.0) if isinstance(result, dict) else 1.0
            
            policy = ConfidencePolicy(ConfidenceThresholds(minimum_threshold=threshold))
            is_valid = await policy.validate_result(score, metadata={"func": func.__name__})
            
            if not is_valid:
                raise ValueError(f"Agent logic rejected due to low confidence: {score}")
                
            return result
        return wrapper
    return decorator