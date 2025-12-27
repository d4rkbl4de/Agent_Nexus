import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from common.schemas.errors import AppError, ErrorCategory, ErrorCode
from common.config.settings import settings
from common.config.logging_config import logger

class InsightViolation(BaseModel):
    constraint_type: str
    message: str
    severity: str
    current_value: Any
    limit: Any

class InsightMateConstraints:
    def __init__(self, agent_id: str, trace_id: str):
        self.agent_id = agent_id
        self.trace_id = trace_id
        self.max_transcript_size_kb = 512
        self.max_processing_time_sec = 60
        self.required_pii_masking = True
        self.allowed_output_formats = ["json", "markdown", "pdf"]
        self.cost_limit_per_analysis = 0.50

    def validate_input(self, transcript_text: str, file_size_kb: float) -> List[InsightViolation]:
        violations = []

        if file_size_kb > self.max_transcript_size_kb:
            violations.append(InsightViolation(
                constraint_type="SIZE_LIMIT_EXCEEDED",
                message=f"Transcript size {file_size_kb}KB exceeds limit of {self.max_transcript_size_kb}KB",
                severity="BLOCKER",
                current_value=file_size_kb,
                limit=self.max_transcript_size_kb
            ))

        if not transcript_text or len(transcript_text.strip()) < 50:
            violations.append(InsightViolation(
                constraint_type="INSUFFICIENT_DATA",
                message="Transcript content is too short for meaningful analysis",
                severity="WARN",
                current_value=len(transcript_text) if transcript_text else 0,
                limit=50
            ))

        return violations

    def check_compliance(self, output_format: str, estimated_cost: float):
        if output_format not in self.allowed_output_formats:
            raise AppError(
                message=f"Unsupported output format: {output_format}",
                category=ErrorCategory.POLICY_VIOLATION,
                code=ErrorCode.BAD_REQUEST,
                trace_id=self.trace_id
            )

        if estimated_cost > self.cost_limit_per_analysis:
            logger.warning(
                f"INSIGHT_COST_WARNING | Agent: {self.agent_id} | Cost: {estimated_cost}",
                trace_id=self.trace_id
            )

    def enforce_runtime_limits(self, elapsed_time: float):
        if elapsed_time > self.max_processing_time_sec:
            logger.error(
                f"INSIGHT_TIMEOUT_ENFORCEMENT | Agent: {self.agent_id}",
                trace_id=self.trace_id
            )
            raise AppError(
                message="Analysis processing time exceeded safety limits",
                category=ErrorCategory.POLICY_VIOLATION,
                code=ErrorCode.LLM_TIMEOUT,
                trace_id=self.trace_id
            )

    def verify_pii_masking(self, content: str) -> bool:
        sensitive_patterns = ["SSN:", "Password:", "Credit Card:"]
        for pattern in sensitive_patterns:
            if pattern in content:
                return False
        return True

    def validate_and_block(self, transcript: str, size: float):
        violations = self.validate_input(transcript, size)
        blockers = [v for v in violations if v.severity == "BLOCKER"]
        
        if blockers:
            primary = blockers[0]
            raise AppError(
                message=primary.message,
                category=ErrorCategory.POLICY_VIOLATION,
                code=ErrorCode.FORBIDDEN,
                details={"all_violations": [v.model_dump() for v in violations]},
                trace_id=self.trace_id
            )