import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from common.config.logging_config import logger
from common.db import POSTGRES_CLIENT
from common.data_sdk.vector_client import VECTOR_DB_CLIENT
from common.agents.internal_tools import INTERNAL_TOOLS
from StudyFlow.tasks import generate_study_plan 

app = FastAPI(
    title="Agent Nexus API Gateway",
    description="Main entry point for all front-end and internal services.",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Gateway service starting up...")
    
    try:
        if POSTGRES_CLIENT.database_url:
            logger.info(f"Postgres Client initialized successfully.")
    except Exception as e:
        logger.error(f"Postgres client failed to initialize: {e}")
        
    try:
        if VECTOR_DB_CLIENT.host:
             logger.info(f"Qdrant Client initialized successfully.")
    except Exception as e:
        logger.error(f"Qdrant client failed to initialize: {e}")

@app.get("/health", summary="Health Check", tags=["System"])
async def health_check():
    return {"status": "ok", "app": "Agent Nexus Gateway"}

@app.post("/tasks/studyflow", summary="Dispatch Study Plan Task", tags=["Tasks"])
async def dispatch_study_plan(topic: str, difficulty: str = "intermediate", user_id: str = "default_user"):
    try:
        message = generate_study_plan.send(
            user_id=user_id,
            topic=topic,
            difficulty=difficulty,
            goal=f"Master {topic} at a {difficulty} level"
        )
        logger.info(f"Dispatched study plan task for {topic}. Message ID: {message.id}")
        return {
            "message": "Study plan generation initiated.",
            "task_id": message.id,
            "status": "queued"
        }
    except Exception as e:
        logger.error(f"Failed to dispatch StudyFlow task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Task dispatch failed: {e}"
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)