import uuid
from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from common.schemas.errors import AppError, ErrorCategory

class ActionType(Enum):
    TOOL_EXECUTION = "TOOL_EXECUTION"
    MEMORY_WRITE = "MEMORY_WRITE"
    EXTERNAL_API = "EXTERNAL_API"
    DELEGATION = "DELEGATION"
    ESCALATION = "ESCALATION"

class ActionProposal(BaseModel):
    proposal_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str
    agent_id: str
    lobe: str
    action_type: ActionType
    payload: Dict[str, Any]
    estimated_cost: float = Field(default=0.0, ge=0.0)
    priority: int = Field(default=1, ge=1, le=5)
    requires_approval: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("trace_id")
    @classmethod
    def validate_trace_context(cls, v: str) -> str:
        if not v or len(v) < 8:
            raise ValueError("Invalid trace context for action proposal")
        return v

class ProposalManager:
    def __init__(self):
        self._registry: Dict[str, ActionProposal] = {}

    async def submit(self, proposal: ActionProposal) -> str:
        if proposal.proposal_id in self._registry:
            raise AppError(
                message=f"Duplicate proposal ID: {proposal.proposal_id}",
                category=ErrorCategory.INTERNAL_ERROR,
                status_code=409
            )
        
        self._registry[proposal.proposal_id] = proposal
        return proposal.proposal_id

    async def get_proposal(self, proposal_id: str) -> ActionProposal:
        proposal = self._registry.get(proposal_id)
        if not proposal:
            raise AppError(
                message="Proposal not found in active registry",
                category=ErrorCategory.NOT_FOUND,
                status_code=404
            )
        return proposal

    async def list_by_trace(self, trace_id: str) -> List[ActionProposal]:
        return [p for p in self._registry.values() if p.trace_id == trace_id]

    async def purge_trace(self, trace_id: str) -> int:
        keys_to_remove = [k for k, v in self._registry.items() if v.trace_id == trace_id]
        for k in keys_to_remove:
            del self._registry[k]
        return len(keys_to_remove)

    async def update_metadata(self, proposal_id: str, updates: Dict[str, Any]) -> None:
        proposal = await self.get_proposal(proposal_id)
        proposal.metadata.update(updates)

proposal_manager = ProposalManager()