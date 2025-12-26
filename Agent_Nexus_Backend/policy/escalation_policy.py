import asyncio
from enum import IntEnum
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from common.config.logging import logger
from tracing.context import get_trace_id, get_agent_id

class EscalationLevel(IntEnum):
    RETRY = 1      
    FALLBACK = 2    
    HUMAN_REQ = 3   
    TERMINATE = 4   

class EscalationPolicy:
    def __init__(self):
        self.error_thresholds = {
            "rate_limit": EscalationLevel.RETRY,
            "context_length_exceeded": EscalationLevel.FALLBACK,
            "insufficient_funds": EscalationLevel.TERMINATE,
            "hallucination_detected": EscalationLevel.HUMAN_REQ,
            "security_violation": EscalationLevel.TERMINATE
        }

    async def determine_action(self, error_type: str, context: Dict[str, Any]) -> EscalationLevel:
        trace_id = get_trace_id()
        agent_id = get_agent_id()
        
        level = self.error_thresholds.get(error_type, EscalationLevel.FALLBACK)
        
        log_msg = (
            f"ESCALATION DETERMINED: Level {level.name} | "
            f"Type: {error_type} | Trace: {trace_id} | Agent: {agent_id}"
        )

        if level >= EscalationLevel.HUMAN_REQ:
            logger.critical(log_msg)
            # Here you would trigger an external notification (n8n/Slack)
        else:
            logger.warning(log_msg)
            
        return level

def handle_escalation(error_type: str):
    def decorator(func):
        policy = EscalationPolicy()
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                action = await policy.determine_action(error_type, {"args": args})
                
                if action == EscalationLevel.TERMINATE:
                    raise SystemExit(f"Policy Enforcement: Terminating trace {get_trace_id()}")
                
                if action == EscalationLevel.HUMAN_REQ:
                    # Logic to park the task in the DB for manual approval
                    logger.info(f"Task parked for manual review: {get_trace_id()}")
                    return {"status": "pending_review", "trace_id": get_trace_id()}
                
                raise e
        return wrapper
    return decorator