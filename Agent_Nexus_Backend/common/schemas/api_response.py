from typing import Any, Dict, List, Optional, Generic, TypeVar
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

T = TypeVar("T")

class ResponseMeta(BaseModel):
    model_config = ConfigDict(frozen=True)
    trace_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    execution_time_ms: Optional[float] = None
    lobe: str

class APIResponse(BaseModel, Generic[T]):
    model_config = ConfigDict(frozen=True)
    success: bool
    data: Optional[T] = None
    error: Optional[Dict[str, Any]] = None
    meta: ResponseMeta

class PaginatedData(BaseModel, Generic[T]):
    model_config = ConfigDict(frozen=True)
    items: List[T]
    total: int
    page: int
    size: int
    has_more: bool

class AgentStreamChunk(BaseModel):
    model_config = ConfigDict(frozen=True)
    chunk_id: str
    trace_id: str
    content: str
    is_final: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

def wrap_success(data: Any, trace_id: str, lobe: str, execution_time: float = 0.0) -> Dict[str, Any]:
    return APIResponse(
        success=True,
        data=data,
        meta=ResponseMeta(
            trace_id=trace_id,
            lobe=lobe,
            execution_time_ms=execution_time
        )
    ).model_dump()

def wrap_error(message: str, code: str, trace_id: str, lobe: str, details: Any = None) -> Dict[str, Any]:
    return APIResponse(
        success=False,
        error={
            "message": message,
            "code": code,
            "details": details
        },
        meta=ResponseMeta(
            trace_id=trace_id,
            lobe=lobe
        )
    ).model_dump()