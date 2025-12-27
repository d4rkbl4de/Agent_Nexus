from enum import Enum
from typing import Optional, Any, Dict
from common.schemas.errors import AppError, ErrorCategory

class AISDKErrorCategory(str, Enum):
    PROMPT_VIOLATION = "PROMPT_VIOLATION"
    CONTEXT_OVERFLOW = "CONTEXT_OVERFLOW"
    OUTPUT_PARSING_FAILED = "OUTPUT_PARSING_FAILED"
    TOOL_DEFINITION_ERROR = "TOOL_DEFINITION_ERROR"
    TOKEN_LIMIT_EXCEEDED = "TOKEN_LIMIT_EXCEEDED"
    INFERENCE_TIMEOUT = "INFERENCE_TIMEOUT"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    MALFORMED_REQUEST = "MALFORMED_REQUEST"
    UNSUPPORTED_MODEL = "UNSUPPORTED_MODEL"

class AISDKException(AppError):
    def __init__(
        self,
        message: str,
        ai_category: AISDKErrorCategory,
        status_code: int = 500,
        retryable: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            category=ErrorCategory.INTERNAL_ERROR,
            status_code=status_code,
            retryable=retryable
        )
        self.ai_category = ai_category
        self.metadata = metadata or {}

class PromptInjectionError(AISDKException):
    def __init__(self, message: str = "Potential prompt injection or adversarial pattern detected"):
        super().__init__(
            message=message,
            ai_category=AISDKErrorCategory.PROMPT_VIOLATION,
            status_code=403,
            retryable=False
        )

class ContextWindowError(AISDKException):
    def __init__(self, token_count: int, limit: int, model_name: str):
        super().__init__(
            message=f"Context window exceeded for {model_name}: {token_count}/{limit}",
            ai_category=AISDKErrorCategory.CONTEXT_OVERFLOW,
            status_code=413,
            retryable=False,
            metadata={"token_count": token_count, "limit": limit, "model": model_name}
        )

class LLMOutputFormatError(AISDKException):
    def __init__(self, expected_schema: str, raw_output: str, reason: Optional[str] = None):
        super().__init__(
            message=f"LLM output validation failed: {reason}" if reason else "LLM failed to return valid structured data",
            ai_category=AISDKErrorCategory.OUTPUT_PARSING_FAILED,
            status_code=422,
            retryable=True,
            metadata={"expected_schema": expected_schema, "raw_output": raw_output}
        )

class ProviderQuotaError(AISDKException):
    def __init__(self, provider: str, reset_time: Optional[float] = None):
        super().__init__(
            message=f"Rate limit or quota exceeded for provider: {provider}",
            ai_category=AISDKErrorCategory.TOKEN_LIMIT_EXCEEDED,
            status_code=429,
            retryable=True,
            metadata={"provider": provider, "reset_time": reset_time}
        )

class InferenceTimeoutError(AISDKException):
    def __init__(self, model_name: str, timeout_val: float):
        super().__init__(
            message=f"Inference timed out for