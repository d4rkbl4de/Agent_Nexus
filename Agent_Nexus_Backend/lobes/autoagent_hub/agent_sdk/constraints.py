import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from common.schemas.errors import AppError, ErrorCategory, ErrorCode
from common.config.settings import settings
from common.config.logging_config import logger

class ConstraintViolation(BaseModel):
    constraint_type: str
    message: str
    severity: str = "BLOCKER"
    current_value: Any
    limit: Any

class AgentConstraints:
    def __init__(self, agent_id: str, trace_id: str):
        self.agent_id = agent_id
        self.trace_id = trace_id
        self.start_time = time.time()
        self.accumulated_cost = 0.0
        self.step_count = 0
        self.max_steps = 15
        self.max_duration = 300 

    def check_policy_compliance(self, prompt: str, tool_calls: List[Any]) -> List[ConstraintViolation]:
        violations = []
        
        if self.step_count >= self.max_steps:
            violations.append(ConstraintViolation(
                constraint_type="STEP_LIMIT",
                message=f"Agent exceeded maximum allowed steps ({self.max_steps})",
                current_value=self.step_count,
                limit=self.max_steps
            ))

        if (time.time() - self.start_time) > self.max_duration:
            violations.append(ConstraintViolation(
                constraint_type="TIMEOUT",
                message="Agent execution duration exceeded safety limit",
                current_value=round(time.time() - self.start_time, 2),
                limit=self.max_duration
            ))

        if self.accumulated_cost > settings.COST_THRESHOLD_DAILY:
            violations.append(ConstraintViolation(
                constraint_type="COST_LIMIT",
                message="Agent reached the maximum daily cost budget",
                current_value=self.accumulated_cost,
                limit=settings.COST_THRESHOLD_DAILY
            ))

        for call in tool_calls:
            if hasattr(call, 'function') and call.function.name.startswith("sys_"):
                violations.append(ConstraintViolation(
                    constraint_type="PERMISSION_DENIED",
                    message=f"Agent attempted to call protected system tool: {call.function.name}",
                    current_value=call.function.name,
                    limit="NON_SYSTEM_TOOLS_ONLY"
                ))

        return violations

    def validate_or_block(self, prompt: str, tool_calls: Optional[List[Any]] = None):
        violations = self.check_policy_compliance(prompt, tool_calls or [])
        if violations:
            primary = violations[0]
            logger.critical(
                f"POLICY_VIOLATION_BLOCK | Agent: {self.agent_id} | Type: {primary.constraint_type}",
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

    def update_usage(self, tokens: int, cost: float):
        self.accumulated_cost += cost
        self.step_count += 1

    def reset(self):
        self.start_time = time.time()
        self.accumulated_cost = 0.0
        self.step_count = 0