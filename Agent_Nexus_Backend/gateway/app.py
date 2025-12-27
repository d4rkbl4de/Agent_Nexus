import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from common.config.logging import logger
from common.schemas.errors import AppError, ErrorCategory
from gateway.dependencies import verify_system_status, get_trace_id

app = FastAPI(
    title="Agent Nexus Hive Mind",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def context_and_perf_middleware(request: Request, call_next):
    trace_id = await get_trace_id(request.headers.get("x-trace-id"))
    request.state.trace_id = trace_id
    start_time = time.perf_counter()
    
    try:
        await verify_system_status()
        response = await call_next(request)
        
        duration = (time.perf_counter() - start_time) * 1000
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Response-Time-MS"] = f"{duration:.2f}"
        
        return response
    except AppError as ae:
        return JSONResponse(
            status_code=ae.status_code,
            content={
                "error": ae.message,
                "category": ae.category.value,
                "trace_id": trace_id,
                "retryable": ae.retryable
            }
        )
    except Exception as e:
        logger.critical(f"UNHANDLED_GATEWAY_ERROR | Trace: {trace_id} | Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal system failure",
                "category": ErrorCategory.INTERNAL_ERROR.value,
                "trace_id": trace_id,
                "retryable": False
            }
        )

@app.get("/health")
async def health_check():
    return {"status": "online", "timestamp": time.time()}

from lobes.insightmate.api import router as insightmate_router
from lobes.studyflow.api import router as studyflow_router
from lobes.chatbuddy.api import router as chatbuddy_router
from lobes.autoagent_hub.api import router as autoagent_router

app.include_router(insightmate_router, prefix="/api/v1/lobes/insightmate", tags=["InsightMate"])
app.include_router(studyflow_router, prefix="/api/v1/lobes/studyflow", tags=["StudyFlow"])
app.include_router(chatbuddy_router, prefix="/api/v1/lobes/chatbuddy", tags=["ChatBuddy+"])
app.include_router(autoagent_router, prefix="/api/v1/lobes/autoagent", tags=["AutoAgent_Hub"])