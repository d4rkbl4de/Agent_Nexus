from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from lobes.insightmate.api.v1.routes import router as v1_router
from lobes.insightmate import lobe
from common.schemas.errors import AppError, ErrorCategory, ErrorCode
from common.config.logging_config import logger
from common.schemas.api_response import wrap_error

def create_app() -> FastAPI:
    app = FastAPI(
        title="Agent Nexus - InsightMate Lobe",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup_event():
        await lobe.start()
        logger.info("INSIGHTMATE_LOBE_ONLINE", lobe="InsightMate", trace_id="SYSTEM_BOOT")

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict()
        )

    @app.exception_handler(Exception)
    async def universal_exception_handler(request: Request, exc: Exception):
        logger.error(f"UNHANDLED_EXCEPTION | {str(exc)}", lobe="InsightMate")
        return JSONResponse(
            status_code=500,
            content=wrap_error(
                message="An internal server error occurred within the InsightMate lobe.",
                code=ErrorCode.SYSTEM_PANIC.value,
                trace_id="N/A",
                lobe="InsightMate"
            )
        )

    app.include_router(v1_router, prefix="/api/v1")

    @app.get("/health")
    async def health_check():
        return await lobe.get_health()

    return app

app = create_app()