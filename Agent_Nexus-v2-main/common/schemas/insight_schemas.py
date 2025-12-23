from typing import TypedDict, List, Literal, Optional
from common.schemas.study_schemas import StudyResource

class InsightAgentState(TypedDict):
    meeting_id: str
    user_id: str
    transcript: str
    summary_text: Optional[str]
    action_items: List[str]
    status: Literal['VALIDATING', 'SUMMARIZING', 'EXTRACTING', 'PERSISTING', 'COMPLETE', 'FAILED']
    resources_created: List[StudyResource]