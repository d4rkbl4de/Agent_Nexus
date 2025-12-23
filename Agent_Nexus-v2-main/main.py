from fastapi import FastAPI
from contextlib import asynccontextmanager

from InsightMate.main import app as insight_app
from StudyFlow.main import app as study_app
from ChatBuddyPlus.main import app as chat_app
from AutoAgent_Hub.main import app as hub_app
from common.db.postgres import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Agent Nexus Gateway (Hive Mind)",
    version="v2.0",
    description="Unified API Gateway for all four specialized AI Lobes.",
    lifespan=lifespan
)

app.mount("/insightmate", insight_app)
app.mount("/studyflow", study_app)
app.mount("/chatbuddy", chat_app)
app.mount("/agenthub", hub_app)

@app.get("/")
async def read_root():
    return {"status": "ok", "message": "Agent Nexus Gateway is operational. Access specific lobes at their mounted paths."}