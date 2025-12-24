from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class ConversationMessage(BaseModel):
    user_id: str
    session_id: str
    message_type: Literal['USER', 'AI', 'TOOL_USE']
    content: str
    timestamp: float = Field(description="Unix timestamp of when the message was recorded.")

class UserProfileSummary(BaseModel):
    user_id: str
    name: str = Field(description="The user's preferred name or alias.")
    summary_id: str = Field(description="A unique ID for this summary record.")
    key_interests: List[str] = Field(description="A list of topics the user frequently discusses.")
    key_facts: List[str] = Field(description="A list of biographical facts or important statements made by the user.")
    last_updated: float = Field(description="Timestamp of the last time this profile summary was generated.")

class ChatResponse(BaseModel):
    user_id: str
    session_id: str
    response_text: str
    memory_update_needed: bool = Field(description="True if the conversation contains new facts or preferences that require updating the UserProfileSummary.")
    next_tool_call: Optional[str] = Field(description="If the agent decides to call a tool, the name of the tool.")