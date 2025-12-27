import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from common.schemas.errors import AppError, ErrorCategory, ErrorCode
from common.config.settings import settings
from common.config.logging_config import logger

class ChatConstraintViolation(BaseModel):
    constraint_type: str
    message: str
    severity: str = "WARN"
    current_value: Any
    limit: Any

class ChatBuddyConstraints:
    def __init__(self, agent_id: str, trace_id: str):
        self.agent_id = agent_id
        self.trace_id = trace_id
        self.start_time = time.time()
        self.accumulated_cost = 0.0
        self.message_count = 0
        self.max_messages_per_turn = 5
        self.max_latency_ms = 15000
        self.blocked_topics = ["illegal_activity", "self_harm", "pii_request"]

    def validate_turn(self, input_text: str, history_depth: int) -> List[ChatConstraintViolation]:
        violations = []

        if history_depth > 50:
            violations.append(ChatConstraintViolation(
                constraint_type="CONTEXT_WINDOW_RISK",
                message="Conversation history exceeds ChatBuddy optimized window",
                current_value=history_depth,
                limit=50
            ))

        if any(topic in input_text.lower() for topic in self.blocked_topics):
            violations.append(ChatConstraintViolation(
                constraint_type="SAFETY_VIOLATION",
                message="Input contains prohibited content according to ChatBuddy policy",
                severity="BLOCKER",
                current_value="Safety Trigger",
                limit="Safe Content Only"
            ))

        if self.accumulated_cost > settings.COST_THRESHOLD_DAILY:
            violations.append(ChatConstraintViolation(
                constraint_type="QUOTA_EXHAUSTED",
                message="Daily spending limit reached for ChatBuddy instance",
                severity="BLOCKER",
                current_value=self.accumulated_cost,
                limit=settings.COST_THRESHOLD_DAILY
            ))

        return violations

    def enforce(self, input_text: str, history_depth: int = 0):
        violations = self.validate_turn(input_text, history_depth)
        
        blockers = [v for v in violations if v.severity == "BLOCKER"]
        if blockers:
            primary = blockers[0]
            logger.error(
                f"CHAT_POLICY_ENFORCEMENT | Agent: {self.agent_id} | Type: {primary.constraint_type}",
                trace_id=self.trace_id,
                extra={"violations": [v.model_dump() for v in violations]}
            )
            raise AppError(
                message=primary.message,
                category=ErrorCategory.POLICY_VIOLATION,
                code=ErrorCode.FORBIDDEN,
                status_code=403,
                details={"violations": [v.model_dump() for v in violations]},
                trace_id=self.trace_id
            )

    def track_usage(self, cost: float):
        self.accumulated_cost += cost
        self.message_count += 1

    def is_healthy(self) -> bool:
        return (time.time() - self.start_time) < (self.max_latency_ms / 1000)