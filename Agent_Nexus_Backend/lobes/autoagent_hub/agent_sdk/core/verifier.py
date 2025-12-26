import asyncio
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from common.config.logging import logger
from common.schemas.errors import AppError
from common.schemas.internal import ToolExecutionResult
from lobes.autoagent_hub.agent_sdk.policies import PolicyEngine

class VerificationResult(BaseModel):
    is_valid: bool
    confidence_score: float = Field(ge=0.0, le=1.0)
    issues: List[str] = Field(default_factory=list)
    suggestions: Optional[str] = None
    verified_at: datetime = Field(default_factory=datetime.utcnow)

class HubVerifier:
    def __init__(self):
        self.policy_engine = PolicyEngine()
        self.min_confidence_threshold = 0.85

    async def verify_mission_outcome(
        self,
        goal: str,
        results: List[ToolExecutionResult],
        agent: Any,
        trace_id: str
    ) -> VerificationResult:
        logger.info(f"VERIFICATION_START | Agent: {agent.id} | Trace: {trace_id}")

        try:
            if not await self._check_verification_policy(agent, trace_id):
                raise AppError.policy_violation(
                    message="Agent unauthorized to perform self-verification",
                    trace_id=trace_id,
                    policy_name="OutcomeVerificationPolicy"
                )

            verification_payload = await agent.reason(
                instruction="""
                As a Verifier, analyze the execution results against the original goal. 
                Identify any hallucinations, security leaks, or logic gaps.
                Return JSON: {
                    "is_valid": bool, 
                    "confidence_score": float, 
                    "issues": list[str], 
                    "suggestions": string
                }
                """,
                context={
                    "original_goal": goal,
                    "execution_history": [r.model_dump() for r in results]
                },
                trace_id=trace_id
            )

            result = VerificationResult(
                is_valid=verification_payload.get("is_valid", False),
                confidence_score=verification_payload.get("confidence_score", 0.0),
                issues=verification_payload.get("issues", []),
                suggestions=verification_payload.get("suggestions")
            )

            if result.confidence_score < self.min_confidence_threshold:
                logger.warning(f"VERIFICATION_LOW_CONFIDENCE | Score: {result.confidence_score} | Trace: {trace_id}")
                result.is_valid = False
                result.issues.append("Confidence score below system threshold.")

            await self._log_verification_metrics(result, agent.id, trace_id)
            
            return result

        except Exception as e:
            logger.error(f"VERIFICATION_CRITICAL_FAILURE | Trace: {trace_id} | Error: {str(e)}")
            return VerificationResult(
                is_valid=False,
                confidence_score=0.0,
                issues=[f"Verification system error: {str(e)}"]
            )

    async def _check_verification_policy(self, agent: Any, trace_id: str) -> bool:
        return await self.policy_engine.check_permission(
            action="verify_outcome",
            resource="verification_engine",
            context={"agent_id": agent.id, "trace_id": trace_id}
        )

    async def _log_verification_metrics(self, result: VerificationResult, agent_id: str, trace_id: str):
        metric_data = {
            "agent_id": agent_id,
            "trace_id": trace_id,
            "valid": result.is_valid,
            "confidence": result.confidence_score,
            "timestamp": result.verified_at.isoformat()
        }
        logger.info(f"VERIFICATION_METRICS | Data: {metric_data}")