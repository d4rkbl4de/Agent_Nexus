import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .tasks import study_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL")

app = FastAPI(
    title="StudyFlow Lobe API",
    description="Specialized agent for generating summaries, study guides, and educational content.",
    version="1.0.0"
)

class LobeRequest(BaseModel):
    user_query: str
    session_id: str
    context: dict = {}

class LobeResponse(BaseModel):
    agent_id: str = "StudyFlow"
    status: str
    task_id: str
    message: str

@app.get("/")
def health_check():
    return {"status": "ok", "service": "StudyFlow Lobe API"}

@app.post("/process", response_model=LobeResponse)
async def process_request(request: LobeRequest):
    if not REDIS_URL:
        raise HTTPException(status_code=500, detail="REDIS_URL is not configured for Dramatiq worker.")
        
    try:
        message = study_task.send(
            request.user_query,
            request.session_id,
            request.context
        )
        
        logger.info(f"StudyFlow task sent: {message.id}")

        return LobeResponse(
            status="QUEUED",
            task_id=message.id,
            message=f"Study task queued with ID: {message.id}"
        )
    except Exception as e:
        logger.error(f"Failed to send StudyFlow task: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate StudyFlow process.")