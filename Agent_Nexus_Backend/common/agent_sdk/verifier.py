from typing import Any, Dict, Optional
from pydantic import BaseModel
from common.config.logging import logger
from common.agent_sdk.planner import PlanStep
from tracing.context import get_trace_id

class VerificationResult(BaseModel):
    is_valid: bool
    reason: Optional[str] = None
    confidence_score: float = 1.0
    should_retry: bool = False

class Verifier:
    def __init__(self, threshold: float = 0.8):
        self.threshold = threshold

    async def verify_step(
        self, 
        step: PlanStep, 
        result: Any, 
        context: Dict[str, Any]
    ) -> VerificationResult:
        trace_id = get_trace_id()
        logger.info(f"VERIFICATION_START | Trace: {trace_id} | Step: {step.step_id}")

        criteria = step.verification_criteria
        
        try:
            if not result:
                return VerificationResult(
                    is_valid=False,
                    reason="Empty result returned from executor.",
                    should_retry=True
                )

            if "required_keys" in criteria:
                for key in criteria["required_keys"]:
                    if key not in result:
                        return VerificationResult(
                            is_valid=False,
                            reason=f"Missing required key: {key}",
                            should_retry=True
                        )

            logger.info(f"VERIFICATION_PASSED | Trace: {trace_id} | Step: {step.step_id}")
            return VerificationResult(is_valid=True)

        except Exception as e:
            logger.error(f"VERIFICATION_ERROR | Trace: {trace_id} | Error: {str(e)}")
            return VerificationResult(
                is_valid=False,
                reason=f"Verifier crash: {str(e)}",
                should_retry=False
            )