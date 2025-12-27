from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from lobes.insightmate.agent_sdk.constraints import InsightMateConstraints, InsightViolation
from common.schemas.errors import AppError, ErrorCategory, ErrorCode
from common.config.logging_config import logger

class VerificationResult(BaseModel):
    is_compliant: bool
    violations: List[InsightViolation] = []
    remediation_advice: Optional[str] = None

class PolicyVerifier:
    def __init__(self, constraints: InsightMateConstraints, trace_id: str):
        self.constraints = constraints
        self.trace_id = trace_id

    async def verify_input_safety(self, transcript: str) -> VerificationResult:
        size_kb = len(transcript.encode('utf-8')) / 1024
        violations = self.constraints.validate_input(transcript, size_kb)
        
        pii_safe = self.constraints.verify_pii_masking(transcript)
        if not pii_safe:
            violations.append(InsightViolation(
                constraint_type="PII_LEAK_DETECTED",
                message="Unmasked sensitive data detected in transcript",
                severity="BLOCKER",
                current_value="Sensitive Content Present",
                limit="Masked/Anonymous"
            ))

        is_compliant = not any(v.severity == "BLOCKER" for v in violations)
        
        return VerificationResult(
            is_compliant=is_compliant,
            violations=violations,
            remediation_advice="Please ensure the transcript is truncated or anonymized if non-compliant."
        )

    async def verify_output_integrity(self, result_data: Dict[str, Any], cost: float) -> bool:
        try:
            output_format = result_data.get("format", "markdown")
            self.constraints.check_compliance(output_format, cost)
            
            if "action_items" in result_data:
                items = result_data["action_items"]
                if not isinstance(items, list):
                    logger.error(f"INTEGRITY_CHECK_FAILED | Action items must be list | Trace: {self.trace_id}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"VERIFICATION_ENGINE_FAULT | {str(e)}", trace_id=self.trace_id)
            return False

    def enforce_policy_or_kill(self, result: VerificationResult):
        if not result.is_compliant:
            blockers = [v for v in result.violations if v.severity == "BLOCKER"]
            primary = blockers[0] if blockers else result.violations[0]
            
            logger.critical(
                f"POLICY_ENFORCEMENT_TERMINATION | Trace: {self.trace_id} | Violation: {primary.constraint_type}",
                extra={"violations": [v.model_dump() for v in result.violations]}
            )
            
            raise AppError(
                message=f"Policy violation prevented execution: {primary.message}",
                category=ErrorCategory.POLICY_VIOLATION,
                code=ErrorCode.FORBIDDEN,
                trace_id=self.trace_id
            )

    async def monitor_runtime(self, start_time: float):
        import time
        elapsed = time.time() - start_time
        self.constraints.enforce_runtime_limits(elapsed)