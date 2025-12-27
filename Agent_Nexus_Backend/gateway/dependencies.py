import time
from typing import AsyncGenerator, Optional
from fastapi import Request, Depends, Header
from common.config.logging import logger
from common.schemas.errors import AppError, ErrorCategory
from policy.kill_switch import kill_switch
from evaluation.metrics import metrics_registry

async def get_trace_id(x_trace_id: Optional[str] = Header(None)) -> str:
    if not x_trace_id:
        import uuid
        x_trace_id = f"tr_{uuid.uuid4().hex[:12]}"
    return x_trace_id

async def verify_system_status():
    if kill_switch.is_halted():
        raise AppError(
            message="System operations are currently suspended by global policy",
            category=ErrorCategory.POLICY_VIOLATION,
            status_code=503,
            retryable=False
        )

async def request_metrics_tracker(
    request: Request,
    trace_id: str = Depends(get_trace_id)
) -> AsyncGenerator[None, None]:
    start_time = time.perf_counter()
    lobe = request.url.path.split("/")[2] if len(request.url.path.split("/")) > 2 else "root"
    
    metrics_registry.start_segment(
        trace_id=trace_id,
        agent_id="gateway",
        lobe=lobe,
        operation=f"{request.method}_{request.url.path}"
    )
    
    try:
        yield
        status = "SUCCESS"
    except Exception:
        status = "FAILURE"
        raise
    finally:
        metrics_registry.stop_segment(
            trace_id=trace_id,
            status=status
        )

async def get_api_key(x_api_key: str = Header(...)) -> str:
    from common.config.secrets import secrets
    if x_api_key != secrets.INTERNAL_API_KEY:
        raise AppError(
            message="Invalid or missing API key",
            category=ErrorCategory.AUTHENTICATION_ERROR,
            status_code=401
        )
    return x_api_key

async def get_current_lobe_context(request: Request) -> str:
    path_parts = request.url.path.lstrip("/").split("/")
    if not path_parts or path_parts[0] != "lobes":
        return "core"
    return path_parts[1]