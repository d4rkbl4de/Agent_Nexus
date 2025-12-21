from typing import Optional

from pydantic import Field

from common.schemas.base import BaseSchema, CommonSchema

class MeetingBase(BaseSchema):
    title: str = Field(..., description="Title or subject of the meeting.")
    duration_minutes: int = Field(..., description="Total duration of the meeting in minutes.")
    summary: Optional[str] = Field(None, description="Concise summary of the meeting content.")
    status: str = Field("pending", description="Processing status (e.g., pending, in_progress, completed, failed).")

class MeetingInDB(CommonSchema, MeetingBase):
    pass
