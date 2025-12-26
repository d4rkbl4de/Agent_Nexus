import time
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from resilience.rate_limit_policy import RateLimiter
from common.config.logging import logger
from tracing.context import get_trace_id

class GatewayRateLimiter(BaseHTTPMiddleware):
    def __init__(
        self, 
        app, 
        requests_per_minute: int = 100, 
        burst_limit: int = 20
    ):
        super().__init__(app)
        self.limiter = RateLimiter(
            resource_name="gateway_global", 
            requests_per_minute=requests_per_minute, 
            burst_limit=burst_limit
        )

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        trace_id = get_trace_id()

        if not await self.limiter.acquire():
            logger.warning(
                f"Gateway Rate Limit Exceeded | IP: {client_ip} | TraceID: {trace_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "trace_id": trace_id,
                    "retry_after": "60s"
                }
            )

        response = await call_next(request)
        return response