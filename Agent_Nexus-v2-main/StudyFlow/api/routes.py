from fastapi import APIRouter, status
from pydantic import BaseModel
from ..tasks import initiate_study_session

router = APIRouter()

class StudyRequest(BaseModel):
    user_id: str
    topic: str

@router.post("/start_session", status_code=status.HTTP_202_ACCEPTED)
async def start_study_session(request: StudyRequest):
    initiate_study_session.send(
        user_id=request.user_id,
        topic=request.topic
    )
    
    return {
        "status": "Task Queued",
        "message": f"Study session for topic '{request.topic}' queued for asynchronous agent processing."
    }

@router.get("/health")
async def get_health():
    return {"status": "ok", "service": "StudyFlow API"}