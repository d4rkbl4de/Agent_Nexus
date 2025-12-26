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
from lobes.autoagent_hub.api.v1.routes import router as v1_hub_router
from lobes.autoagent_hub.agent_sdk.registry import HubAgentRegistry

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("LOBE_BOOTUP_START | Lobe: AutoAgent_Hub")
    try:
        registry = HubAgentRegistry()
        await registry.initialize_agents()
        app.state.registry = registry
        logger.info("LOBE_BOOTUP_COMPLETE | Lobe: AutoAgent_Hub")
        yield
    except Exception as e:
        logger.critical(f"LOBE_BOOTUP_CRITICAL_FAILURE | Lobe: AutoAgent_Hub | Error: {str(e)}")
        raise
    finally:
        logger.info("LOBE_SHUTDOWN_START | Lobe: AutoAgent_Hub")

def create_hub_app() -> FastAPI:
    app = FastAPI(
        title="Agent Nexus Hive Mind - AutoAgent_Hub",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/api/autoagent/docs",
        openapi_url="/api/autoagent/openapi.json"
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
        response.headers["X-Process-Time"] = str(process_time)
        return response

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=status.HTTP_400_