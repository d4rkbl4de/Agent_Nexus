import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from common.schemas.errors import AppError, ErrorCategory, ErrorCode
from common.config.logging_config import logger

class StudyConstraintViolation(BaseModel):
    constraint_type: str
    message: str
    severity: str
    current_val: Any
    limit_val: Any

class StudyFlowConstraints:
    def __init__(self, agent_id: str, trace_id: str):
        self.agent_id = agent_id
        self.trace_id = trace_id
        self.max_material_pages = 50
        self.max_questions_per_session = 20
        self.prohibited_topics = ["violence", "unauthorized_code_execution", "plagiarism_tools"]
        self.cost_limit_per_session = 0.25
        self.session_timeout_seconds = 1800

    def validate_study_material(self, content_length: int, topic: str) -> List[StudyConstraintViolation]:
        violations = []
        
        if any(prohibited in topic.lower() for prohibited in self.prohibited_topics):
            violations.append(StudyConstraintViolation(
                constraint_type="TOPIC_RESTRICTION",
                message=f"Topic '{topic}' violates safety guidelines for educational content.",
                severity="BLOCKER",
                current_val=topic,
                limit_val="Allowed Curriculum"
            ))

        if content_length > (self.max_material_pages * 3000):
            violations.append(StudyConstraintViolation(
                constraint_type="CONTENT_OVERFLOW",
                message="Study material size exceeds processing limits for a single session.",
                severity="BLOCKER",
                current_val=content_length,
                limit_val=self.max_material_pages * 3000
            ))

        return violations

    def check_pedagogical_integrity(self, session_depth: str, question_count: int):
        if question_count > self.max_questions_per_session:
            raise AppError(
                message=f"Question limit ({self.max_questions_per_session}) exceeded for session stability.",
                category=ErrorCategory.POLICY_VIOLATION,
                code=ErrorCode.BAD_REQUEST,
                trace_id=self.trace_id
            )

    def verify_session_budget(self, current_cost: float):
        if current_cost > self.cost_limit_per_session:
            logger.critical(
                f"STUDY_BUDGET_EXCEEDED | Agent: {self.agent_id} | Cost: {current_cost}",
                trace_id=self.trace_id
            )
            raise AppError(
                message="Session budget limit reached. Please summarize and conclude.",
                category=ErrorCategory.POLICY_VIOLATION,
                code=ErrorCode.FORBIDDEN,
                trace_id=self.trace_id
            )

    def validate_and_block(self, content: str, topic: str):
        violations = self.validate_study_material(len(content), topic)
        blockers = [v for v in violations if v.severity == "BLOCKER"]
        
        if blockers:
            primary = blockers[0]
            raise AppError(
                message=primary.message,
                category=ErrorCategory.POLICY_VIOLATION,
                code=ErrorCode.FORBIDDEN,
                details={"violations": [v.model_dump() for v in violations]},
                trace_id=self.trace_id
            )

    def check_runtime_compliance(self, start_time: float):
        elapsed = time.time() - start_time
        if elapsed > self.session_timeout_seconds:
            raise AppError(
                message="Study session duration exceeded safety limits.",
                category=ErrorCategory.POLICY_VIOLATION,
                code=ErrorCode.LLM_TIMEOUT,
                trace_id=self.trace_id
            )