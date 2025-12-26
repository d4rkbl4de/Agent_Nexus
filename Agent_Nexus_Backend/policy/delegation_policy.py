import asyncio
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from common.config.logging import logger
from tracing.context import get_trace_id, get_agent_id

class DelegationContract(BaseModel):
    source_lobe: str
    target_lobe: str
    priority: int = Field(default=1, ge=1, le=5)
    capability_required: str
    max_handoffs: int = Field(default=3)

class DelegationPolicy:
    def __init__(self):
        self.allowed_routes = {
            "autoagent": ["insightmate", "studyflow", "chatbuddy"],
            "insightmate": ["chatbuddy"],
            "studyflow": ["insightmate"],
            "chatbuddy": []
        }
        self._handoff_counter: Dict[str, int] = {}

    async def authorize_delegation(self, contract: DelegationContract) -> bool:
        trace_id = get_trace_id()
        
        if contract.target_lobe not in self.allowed_routes.get(contract.source_lobe, []):
            logger.error(
                f"DELEGATION VIOLATION: Unauthorized lobe handoff attempted. "
                f"{contract.source_lobe} -> {contract.target_lobe} | TraceID: {trace_id}"
            )
            return False

        current_handoffs = self._handoff_counter.get(trace_id, 0)
        if current_handoffs >= contract.max_handoffs:
            logger.critical(
                f"DELEGATION RECURSION: Max handoffs reached (Rule 14). "
                f"TraceID: {trace_id} | Limit: {contract.max_handoffs}"
            )
            return False

        self._handoff_counter[trace_id] = current_handoffs + 1
        logger.info(
            f"Delegation Authorized: {contract.source_lobe} delegating '{contract.capability_required}' "
            f"to {contract.target_lobe}. Handoff: {self._handoff_counter[trace_id]}"
        )
        return True

def delegate_task(target_lobe: str, capability: str):
    def decorator(func):
        policy = DelegationPolicy()
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            source = get_agent_id() or "unknown"
            contract = DelegationContract(
                source_lobe=source,
                target_lobe=target_lobe,
                capability_required=capability
            )
            
            if not await policy.authorize_delegation(contract):
                raise PermissionError(f"Delegation to {target_lobe} rejected by Control Plane.")
                
            return await func(*args, **kwargs)
        return wrapper
    return decorator