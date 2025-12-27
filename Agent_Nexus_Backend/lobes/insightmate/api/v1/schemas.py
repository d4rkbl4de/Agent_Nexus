from typing import List, Optional, Dict, Any
from pydantic import Field
from common.schemas.base import BaseSchema, TraceableSchema

class ActionItem(BaseSchema):
    task: str
    owner: Optional[str] = "Unassigned"
    deadline: Optional[str] = None
    priority: str = Field(default="medium", pattern="^(high|medium|low)$")
    status: str = "pending"

class InsightSummary(BaseSchema):
    executive_summary: str
    key_decisions: List[str] = Field(default_factory=list)
    outcomes: List[str] = Field(default_factory=list)

class AnalysisResult(BaseSchema):
    summary: Optional[InsightSummary] = None
    action_items: List[ActionItem] = Field(default_factory=list)
    sentiment_trends: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AnalysisRequest(TraceableSchema):
    agent_id: str
    transcript: str
    participants: List[str] = Field(default_factory=list)
    output_format: str = "markdown"
    tasks: List[str] = Field(
        default=["generate_meeting_summary", "extract_action_items"],
        description="Specific task IDs to execute"
    )

class AnalysisSessionResponse(BaseSchema):
    session_id: str
    trace_id: str
    status: str
    estimated_completion_ms: int

class AnalysisDetailResponse(BaseSchema):
    session_id: str
    agent_id: str
    status: str
    result: Optional[AnalysisResult] = None
    errors: List[Dict[str, Any]] = Field(default_factory=list)

class LobeHealthResponse(BaseSchema):
    lobe: str = "InsightMate"
    status: str
    active_workers: int
    queue_depth: int