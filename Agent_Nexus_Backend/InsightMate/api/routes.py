from fastapi import APIRouter, status
from pydantic import BaseModel
from ..tasks import process_meeting_data

router = APIRouter()

class MeetingData(BaseModel):
    meeting_id: str
    transcript_text: str
    user_id: str

@router.post("/process", status_code=status.HTTP_202_ACCEPTED)
async def submit_meeting_data(data: MeetingData):
    process_meeting_data.send(
        meeting_id=data.meeting_id,
        transcript_text=data.transcript_text,
        user_id=data.user_id
    )
    
    return {
        "status": "Task Queued",
        "message": f"Meeting {data.meeting_id} queued for asynchronous processing."
    }

@router.get("/health")
async def get_health():
    return {"status": "ok", "service": "InsightMate API"}