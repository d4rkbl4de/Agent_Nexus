from typing import Any, Dict, Optional, Generic, TypeVar, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

T = TypeVar("T")

class ErrorCategory(str, Enum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    NOT_FOUND_ERROR = "NOT_FOUND_ERROR"
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    CIRCUIT_BREAKER_OPEN = "CIRCUIT_BREAKER_OPEN"

class ErrorCode(str, Enum):
    INVALID_INPUT = "AN-001"
    UNAUTHORIZED = "AN-002"
    FORBIDDEN = "AN-003"
    RESOURCE_NOT_FOUND = "AN-004"
    LLM_TIMEOUT = "AN-005"
    TOKEN_EXHAUSTED = "AN-006"
    SYSTEM_PANIC = "AN-007"
    TRACE_CONTEXT_MISSING = "AN-008"
    MEMORY_RETRIEVAL_FAILED = "AN-009"
    TASK_QUEUE_FULL = "AN-010"

class AppError(Exception):
    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        code: ErrorCode = ErrorCode.SYSTEM_PANIC,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.category = category
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        self.trace_id = trace_id
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": False,
            "error": {
                "category": self.category.value,
                "code": self.code.value,
                "message": self.message,
                "details": self.details
            },
            "meta": {
                "trace_id": self.trace_id,
                "timestamp": self.timestamp.isoformat()
            }
        }

class BaseSchema(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        from_attributes=True
    )

class TraceableSchema(BaseSchema):
    trace_id: str = Field(..., description="Mandatory Rule 20 Trace ID")
    lobe: str = Field(..., pattern="^(InsightMate|StudyFlow|ChatBuddy|AutoAgent_Hub|CORE)$")

class AgentContext(TraceableSchema):
    agent_id: str
    session_id: str
    request_depth: int = 0
    priority: int = 1

class ExecutionMetadata(BaseSchema):
    start_time: datetime = Field(default_factory=datetime.utcnow)
    provider: str
    model_name: str
    tokens_consumed: int = 0
    cost: float = 0.0

from common.schemas.api_response import (
    APIResponse,
    ResponseMeta,
    PaginatedData,
    AgentStreamChunk,
    wrap_success,
    wrap_error
)

__all__ = [
    "ErrorCategory",
    "ErrorCode",
    "AppError",
    "BaseSchema",
    "TraceableSchema",
    "AgentContext",
    "ExecutionMetadata",
    "APIResponse",
    "ResponseMeta",
    "PaginatedData",
    "AgentStreamChunk",
    "wrap_success",
    "wrap_error"
]