from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import Field
from common.schemas.base import BaseNexusModel

class ErrorCategory(str, Enum):
    VALIDATION = "VALIDATION_ERROR"
    AUTHENTICATION = "AUTH_ERROR"
    AUTHORIZATION = "PERMISSION_ERROR"
    INFRASTRUCTURE = "INFRA_ERROR"
    AGENTIC_FAILURE = "AGENT_ERROR"
    POLICY_VIOLATION = "POLICY_ERROR"
    NOT_FOUND = "RESOURCE_NOT_FOUND"
    CONFLICT = "STATE_CONFLICT"
    RATE_LIMIT = "RATE_LIMIT_EXCEEDED"
    INTERNAL = "INTERNAL_SERVER_ERROR"

class ErrorDetail(BaseNexusModel):
    code: str
    message: str
    target: Optional[str] = Field(None, description="The specific field or resource causing the error")
    details: Optional[Dict[str, Any]] = None

class AppError(BaseNexusModel):
    category: ErrorCategory
    error: ErrorDetail
    trace_id: str
    recoverable: bool = False
    action_required: Optional[str] = None
    
    @classmethod
    def validation_error(cls, message: str, trace_id: str, details: List[Dict[str, Any]]) -> "AppError":
        return cls(
            category=ErrorCategory.VALIDATION,
            trace_id=trace_id,
            error=ErrorDetail(
                code="VAL_422",
                message=message,
                details={"errors": details}
            )
        )

    @classmethod
    def policy_violation(cls, message: str, trace_id: str, policy_name: str) -> "AppError":
        return cls(
            category=ErrorCategory.POLICY_VIOLATION,
            trace_id=trace_id,
            error=ErrorDetail(
                code="POLICY_001",
                message=message,
                target=policy_name
            ),
            recoverable=False
        )

    @classmethod
    def agent_failure(cls, message: str, trace_id: str, agent_id: str) -> "AppError":
        return cls(
            category=ErrorCategory.AGENTIC_FAILURE,
            trace_id=trace_id,
            error=ErrorDetail(
                code="AGENT_500",
                message=message,
                target=agent_id
            ),
            recoverable=True,
            action_required="RETRY_WITH_CONTEXT"
        )