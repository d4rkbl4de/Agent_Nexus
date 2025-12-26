import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from tracing.context import set_trace_context, clear_trace_context
from tracing.exporters import trace_exporter
from common.config.logging import logger

class TraceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        agent_id = request.headers.get("X-Agent-ID")
        task_id = request.headers.get("X-Task-ID")

        set_trace_context(trace_id=trace_id, agent_id=agent_id, task_id=task_id)

        start_time = time.perf_counter()
        
        await trace_exporter.export_span(
            name="request_start",
            payload={
                "method": request.method,
                "url": str(request.url),
                "client_host": request.client.host if request.client else None
            },
            level="INFO"
        )

        try:
            response = await call_next(request)
            process_time = (time.perf_counter() - start_time) * 1000
            response.headers["X-Trace-ID"] = trace_id
            response.headers["X-Process-Time-MS"] = str(round(process_time, 2))

            await trace_exporter.export_span(
                name="request_success",
                payload={
                    "status_code": response.status_code,
                    "process_time_ms": round(process_time, 2)
                },
                level="INFO"
            )
            return response

        except Exception as e:
            process_time = (time.perf_counter() - start_time) * 1000
            logger.exception(f"Unhandled middleware exception: {str(e)}")
            
            await trace_exporter.export_span(
                name="request_failure",
                payload={
                    "error": type(e).__name__,
                    "message": str(e),
                    "process_time_ms": round(process_time, 2)
                },
                level="ERROR"
            )
            raise e
        finally:
            clear_trace_context()