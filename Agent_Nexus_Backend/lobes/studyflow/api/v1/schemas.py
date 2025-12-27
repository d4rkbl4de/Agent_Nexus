from typing import List, Optional, Dict, Any
from pydantic import Field
from common.schemas.base import BaseSchema, TraceableSchema

class KnowledgeGapSchema(BaseSchema):
    topic: str
    confidence_score: float
    remediation_status: str
    last_assessed: str

class StudySessionRequest(TraceableSchema):
    user_id: str
    agent_id: str
    subject: str
    goals: str
    difficulty: str = Field(default="intermediate", pattern="^(beginner|intermediate|advanced)$")

class StudySessionResponse(BaseSchema):
    session_id: str
    status: str
    trace_id: str
    estimated_ready_in_sec: int = 5

class TutorInteractionRequest(TraceableSchema):
    user_id: str
    agent_id: str
    message: str
    context_window: List[Dict[str, str]] = Field(default_factory=list)

class EvaluationSchema(BaseSchema):
    confidence_level: float
    understanding_depth: str
    detected_gaps: List[str]
    misconceptions: List[str]
    reasoning: str

class TutorInteractionResponse(BaseSchema):
    session_id: str
    response: str
    evaluation: EvaluationSchema
    next_step: Optional[str] = None

class CurriculumResponse(BaseSchema):
    session_id: str
    subject: str
    pathway: List[str]
    completed: List[str]
    gaps: List[str]

class KnowledgeStateResponse(BaseSchema):
    user_id: str
    subject: str
    overall_mastery: float
    detailed_gaps: List[KnowledgeGapSchema]