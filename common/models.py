from pydantic import BaseModel, Field
from typing import List

class AnalysisResult(BaseModel):
    summary: str = Field(description="A concise summary of the meeting, focusing on decisions and key takeaways.")
    action_items: List[str] = Field(description="A list of specific, executable action items assigned to individuals. Each item must start with the assignee (e.g., 'Jane: Prepare detailed report...').")
    is_valid: bool = Field(description="Set to true if the transcript contains enough information (decisions, actions, or clear discussion points) to generate a useful summary, otherwise false.")