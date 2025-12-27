from typing import List, Optional, Dict, Any
from pydantic import Field
from common.schemas.base import BaseSchema, TraceableSchema

class AgentMetadata(BaseSchema):
    agent_id: str
    name: str
    version: str
    description: Optional[str] = None
    tools_enabled: List[str] = Field(default_factory=list)
    personality_traits: List[str] = Field(default_factory=list, alias="personality")

class ChatRequest(TraceableSchema):
    session_id: str = Field(..., description="Unique ID for the conversation thread")
    agent_id: str = Field(..., description="Target ChatBuddy agent ID")
    user_id: str = Field(..., description="External user identifier")
    message: str = Field(..., min_length=1, max_length=4000)
    context_overrides: Optional[Dict[str, Any]] = None

class ChatSessionResponse(BaseSchema):
    session_id: str
    trace_id: str
    agent_metadata: AgentMetadata
    created_at: str = Field(default_factory=lambda: "2025-12-27T18:32:50Z")

class ChatHistoryItem(BaseSchema):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

class ChatHistoryResponse(BaseSchema):
    session_id: str
    history: List[ChatHistoryItem]
    total_messages: int

class SessionTerminationResponse(BaseSchema):
    session_id: str
    status: str = "terminated"
    summary_generated: bool = False