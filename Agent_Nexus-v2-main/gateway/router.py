from fastapi import APIRouter, HTTPException, status, Header
from typing import Optional
import uuid

from common.logger import logger
from common.db.postgres import db_client
from common.data_sdk.vector_client import vector_client
from StudyFlow.tasks import generate_study_plan

router = APIRouter()

@router.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "operational",
        "service": "agent_nexus_gateway",
        "db_connected": db_client.is_active(),
        "vector_db_connected": vector_client.is_active()
    }

@router.post("/tasks/studyflow", status_code=status.HTTP_202_ACCEPTED, tags=["Learning"])
async def dispatch_study_plan(
    topic: str, 
    difficulty: str = "intermediate", 
    user_id: str = "default_user",
    x_trace_id: Optional[str] = Header(None)
):
    trace_id = x_trace_id or str(uuid.uuid4())
    
    try:
        task = generate_study_plan.send(
            user_id=user_id,
            topic=topic,
            difficulty=difficulty,
            trace_id=trace_id
        )
        
        logger.info(f"TASK_QUEUED | trace_id={trace_id} | lobe=StudyFlow | task_id={task.id}")
        
        return {
            "task_id": task.id,
            "trace_id": trace_id,
            "status": "accepted",
            "message": f"Study plan generation for {topic} is now in the queue."
        }
        
    except Exception as e:
        logger.error(f"TASK_ERROR | trace_id={trace_id} | err={str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reach the task broker."
        )