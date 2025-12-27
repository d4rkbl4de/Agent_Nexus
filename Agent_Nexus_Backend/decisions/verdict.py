import asyncio
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from common.config.logging import logger
from common.schemas.errors import AppError, ErrorCategory
from evaluation.scoring import quality_scorer
from policy.kill_switch import kill_switch

class VerdictStatus(Enum):
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    ESCALATED = "ESCALATED"
    HALTED = "HALTED"
    ERROR = "ERROR"

class DecisionVerdict(BaseModel):
    proposal_id: str
    trace_id: str
    status: VerdictStatus
    reasoning: str
    enforced_by: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PolicyEngine:
    def __init__(self, cost_limit: float = 2.0, min_score: float = 0.8):
        self.cost_limit = cost_limit
        self.min_score = min_score
        self.scorer = quality_scorer
        self.kill_switch = kill_switch

    async def evaluate_proposal(self, proposal: Any) -> DecisionVerdict:
        try:
            if self.kill_switch.is_halted():
                return DecisionVerdict(
                    proposal_id=proposal.proposal_id,
                    trace_id=proposal.trace_id,
                    status=VerdictStatus.HALTED,
                    reasoning="Global system halt active",
                    enforced_by="policy.kill_switch"
                )

            if proposal.estimated_cost > self.cost_limit:
                return DecisionVerdict(
                    proposal_id=proposal.proposal_id,
                    trace_id=proposal.trace_id,
                    status=VerdictStatus.ESCALATED,
                    reasoning=f"Cost {proposal.estimated_cost} exceeds limit {self.cost_limit}",
                    enforced_by="policy.budget_control"
                )

            quality_validation = await self.scorer.compute_score(
                trace_id=proposal.trace_id,
                raw_output=proposal.payload,
                criteria={"logic": 0.7, "safety": 0.3}
            )

            if not quality_validation.passed:
                return DecisionVerdict(
                    proposal_id=proposal.proposal_id,
                    trace_id=proposal.trace_id,
                    status=VerdictStatus.DENIED,
                    reasoning=f"Quality score {quality_validation.aggregate_score} below threshold {self.min_score}",
                    enforced_by="evaluation.quality_gate",
                    metadata={"scores": [c.model_dump() for c in quality_validation.components]}
                )

            return DecisionVerdict(
                proposal_id=proposal.proposal_id,
                trace_id=proposal.trace_id,
                status=VerdictStatus.APPROVED,
                reasoning="Proposal satisfies all constitutional constraints",
                enforced_by="policy.root"
            )

        except Exception as e:
            logger.critical(f"POLICY_ENGINE_ERROR | Trace: {proposal.trace_id} | Error: {str(e)}")
            return DecisionVerdict(
                proposal_id=proposal.proposal_id,
                trace_id=proposal.trace_id,
                status=VerdictStatus.ERROR,
                reasoning=f"Internal policy evaluation failure: {str(e)}",
                enforced_by="policy.system_exception"
            )

    def update_limits(self, cost_limit: Optional[float] = None, min_score: Optional[float] = None):
        if cost_limit is not None:
            self.cost_limit = cost_limit
        if min_score is not None:
            self.min_score = min_score

policy_engine = PolicyEngine()