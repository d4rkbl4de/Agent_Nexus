import asyncio
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from common.config.logging import logger
from evaluation.scoring import quality_scorer
from policy.kill_switch import kill_switch

class VerdictStatus(Enum):
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    ESCALATED = "ESCALATED"
    HALTED = "HALTED"

class DecisionVerdict(BaseModel):
    proposal_id: str
    trace_id: str
    status: VerdictStatus
    reasoning: str
    enforced_by: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PolicyEngine:
    def __init__(self):
        self.scorer = quality_scorer
        self.kill_switch = kill_switch

    async def evaluate_proposal(self, proposal: Any) -> DecisionVerdict:
        if self.kill_switch.is_halted():
            return DecisionVerdict(
                proposal_id=proposal.proposal_id,
                trace_id=proposal.trace_id,
                status=VerdictStatus.HALTED,
                reasoning="Global Kill Switch is active",
                enforced_by="policy.kill_switch"
            )

        if proposal.estimated_cost > 1.0:
            return DecisionVerdict(
                proposal_id=proposal.proposal_id,
                trace_id=proposal.trace_id,
                status=VerdictStatus.ESCALATED,
                reasoning="Cost exceeds single-turn budget",
                enforced_by="policy.budget_control"
            )

        try:
            quality_validation = await self.scorer.compute_score(
                trace_id=proposal.trace_id,
                raw_output=proposal.payload,
                criteria={"logic": 0.6, "safety": 0.4}
            )

            if not quality_validation.passed:
                return DecisionVerdict(
                    proposal_id=proposal.proposal_id,
                    trace_id=proposal.trace_id,
                    status=VerdictStatus.DENIED,
                    reasoning=f"Quality score {quality_validation.aggregate_score} below threshold",
                    enforced_by="evaluation.quality_gate"
                )

            return DecisionVerdict(
                proposal_id=proposal.proposal_id,
                trace_id=proposal.trace_id,
                status=VerdictStatus.APPROVED,
                reasoning="All policy checks passed",
                enforced_by="policy.root"
            )

        except Exception as e:
            logger.error(f"VERDICT_CRITICAL_FAILURE | Trace: {proposal.trace_id} | Error: {str(e)}")
            return DecisionVerdict(
                proposal_id=proposal.proposal_id,
                trace_id=proposal.trace_id,
                status=VerdictStatus.DENIED,
                reasoning=f"Internal policy engine error: {str(e)}",
                enforced_by="policy.system"
            )

policy_engine = PolicyEngine()