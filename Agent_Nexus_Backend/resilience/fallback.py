import functools
import asyncio
from typing import Callable, Any, Optional, Type, Union, Dict
from common.config.logging import logger
from tracing.context import get_trace_id, get_agent_id

class FallbackHandler:
    def __init__(
        self,
        fallback_func: Callable,
        exceptions: tuple = (Exception,),
        agent_id: Optional[str] = None
    ):
        self.fallback_func = fallback_func
        self.exceptions = exceptions
        self.agent_id = agent_id

    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except self.exceptions as e:
            trace_id = get_trace_id()
            current_agent = self.agent_id or get_agent_id()
            
            logger.error(
                f"Primary execution failed. Initiating Agentic Fallback (Rule 18). "
                f"TraceID: {trace_id} | Agent: {current_agent} | Error: {str(e)}"
            )

            try:
                if asyncio.iscoroutinefunction(self.fallback_func):
                    return await self.fallback_func(*args, **kwargs)
                return self.fallback_func(*args, **kwargs)
            except Exception as fallback_err:
                logger.critical(
                    f"Critical Failure: Fallback logic failed (Rule 14). "
                    f"TraceID: {trace_id} | Error: {str(fallback_err)}"
                )
                raise fallback_err

def fallback(fallback_func: Callable, exceptions: tuple = (Exception,)):
    def decorator(func: Callable):
        handler = FallbackHandler(fallback_func, exceptions)
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await handler.execute(func, *args, **kwargs)
        return wrapper
    return decorator

async def llm_model_downgrade_fallback(*args, **kwargs):
    from common.llm.client import llm_client
    kwargs['model'] = "gpt-4o-mini"
    logger.info("Failing over to secondary model: gpt-4o-mini (Rule 18)")
    return await llm_client.generate(*args, **kwargs)

async def static_empty_response_fallback(*args, **kwargs):
    return {"status": "error", "message": "Service temporarily degraded", "data": []}