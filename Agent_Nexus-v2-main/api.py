from fastapi import FastAPI
from InsightMate.api import app as insightmate_app
from StudyFlow.api import app as studyflow_app

app = FastAPI(
    title="Agent Nexus API",
    version="0.1.0",
    description="The central gateway for the InsightMate and StudyFlow specialized AI Lobes.",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.mount("/insightmate", insightmate_app, name="insightmate")

app.mount("/studyflow", studyflow_app, name="studyflow")

@app.get("/healthz")
async def health_check():
    return {"status": "ok", "message": "Agent Nexus Gateway operational"}