import uuid
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from tracing.context import set_trace_id, set_agent_id
from common.config.logging import logger

class TracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        trace_id = request.headers.get("X-Trace-ID") or str(uuid.uuid4())
        agent_id = request.headers.get("X-Agent-ID", "gateway")
        
        set_trace_id(trace_id)
        set_agent_id(agent_id)
        
        logger.info(
            f"Incoming Request | Method: {request.method} | Path: {request.url.path} | "
            f"TraceID: {trace_id} | Agent: {agent_id}"
        )

        try:
            response: Response = await call_next(request)
            
            process_time = time.perf_counter() - start_time
            response.headers["X-Trace-ID"] = trace_id
            response.headers["X-Process-Time"] = str(process_time)
            
            logger.info(
                f"Request Completed | Status: {response.status_code} | "
                f"Duration: {process_time:.4f}s | TraceID: {trace_id}"
            )
            
            return response
            
        except Exception as e:
            process_time = time.perf_counter() - start_time
            logger.error(
                f"Request Failed | Error: {str(e)} | "
                f"Duration: {process_time:.4f}s | TraceID: {trace_id}"
            )
            raise e