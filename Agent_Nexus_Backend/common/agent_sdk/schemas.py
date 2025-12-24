from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class MeetingTranscript(BaseModel):
    """Schema for the input meeting transcript."""
    transcript_text: str = Field(..., description="The full, raw text of the meeting transcript.")
    user_id: str = Field(..., description="The ID of the user submitting the transcript.")

class ActionItem(BaseModel):
    """A detailed action item extracted from the transcript."""
    task_description: str = Field(..., description="A clear, actionable description of the task.")
    assigned_to: str = Field(default="Unassigned", description="The person or team responsible for the task.")
    due_date: str = Field(default="TBD", description="The suggested due date (use natural language).")

class AnalysisResult(BaseModel):
    """The structured output schema for the AI agent's analysis."""
    summary: str = Field(..., description="A concise, high-level summary of the meeting, suitable for an executive.")
    key_decisions: List[str] = Field(default_factory=list, description="List of 3-5 main decisions made.")
    action_items: List[ActionItem] = Field(default_factory=list, description="Detailed list of tasks extracted from the meeting.")


class AgentState(BaseModel):
    """Base state for the LangGraph agent."""
    transcript: str = Field(..., description="The current transcript being processed.")
    analysis_result: Optional[AnalysisResult] = None
    next_step: str = "summarize"
