import os
import uuid
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from common.config.logging import logger
from common.schemas.api_response import APIResponse
from common.schemas.errors import AppError, ErrorCategory, ErrorDetail
from lobes.chatbuddy.api.v1.routes import router as v1_chat_router
from lobes.chatbuddy.agent_sdk.registry import ChatAgentRegistry

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("LOBE_BOOTUP_START | Lobe: ChatBuddy")
    try:
        registry = ChatAgentRegistry()
        await registry.initialize_agents()
        app.state.registry = registry
        logger.info("LOBE_BOOTUP_COMPLETE | Lobe: ChatBuddy")
        yield
    except Exception as e:
        logger.critical(f"LOBE_BOOTUP_CRITICAL_FAILURE | Lobe: ChatBuddy | Error: {str(e)}")
        raise
    finally:
        logger.info("LOBE_SHUTDOWN_START | Lobe: ChatBuddy")

def create_chat_app() -> FastAPI:
    app = FastAPI(
        title="Agent Nexus Hive Mind - ChatBuddy+",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/api/chatbuddy/docs",
        openapi_url="/api/chatbuddy/openapi.json"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def trace_context_middleware(request: Request, call_next):
        start_time = time.time()
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        request.state.trace_id = trace_id
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        return response

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=APIResponse(
                success=False,
                trace_id=request.state.trace_id,
                error=exc
            ).model_dump()
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        trace_id = getattr(request.state, "trace_id", str(uuid.uuid4()))
        logger.error(f"UNHANDLED_CHAT_EXCEPTION | Trace: {trace_id} | Error: {str(exc)}")
        
        error_detail = AppError(
            category=ErrorCategory.INTERNAL,
            trace_id=trace_id,
            error=ErrorDetail(
                code="CHAT_INTERNAL_500",
                message="An unexpected error occurred within the ChatBuddy Lobe."
            )
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=APIResponse(
                success=False,
                trace_id=trace_id,
                error=error_detail
            ).model_dump()
        )

    app.include_router(v1_chat_router, prefix="/api/v1/chat")

    @app.get("/health", tags=["System"])
    async def health_check():
        return APIResponse(
            success=True,
            data={
                "status": "online",
                "lobe": "chatbuddy",
                "features": ["nlp", "streaming", "memory_sync"]
            }
        )

    return app

app = create_chat_app()