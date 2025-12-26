import asyncio
import uuid
import time
from typing import Any, Dict, List, Optional
from datetime import datetime

from common.config.logging import logger
from common.schemas.internal import ToolExecutionCall, ToolExecutionResult
from common.schemas.errors import AppError, ErrorCategory
from common.messaging.publisher import MessagePublisher

class OrchestrationExecutor:
    def __init__(self):
        self.publisher = MessagePublisher()

    async def execute_step(
        self, 
        step: Any, 
        agent: Any, 
        trace_id: str
    ) -> ToolExecutionResult:
        step_id = getattr(step, "id", str(uuid.uuid4()))
        logger.info(f"STEP_EXECUTION_START | Agent: {agent.id} | Step: {step_id} | Trace: {trace_id}")
        
        start_time = time.time()
        
        try:
            if not await self._validate_policy(step, agent, trace_id):
                raise AppError.policy_violation(
                    message=f"Step execution denied by policy for agent {agent.id}",
                    trace_id=trace_id,
                    policy_name="ExecutionSafetyPolicy"
                )

            tool_call = ToolExecutionCall(
                tool_name=step.tool_name,
                arguments=step.args,
                caller_id=agent.id,
                trace_id=trace_id
            )

            result_data = await agent.call_tool(tool_call)
            
            execution_time = (time.time() - start_time) * 1000
            
            result = ToolExecutionResult(
                tool_name=step.tool_name,
                output=result_data,
                is_error=False,
                execution_time_ms=execution_time,
                trace_id=trace_id
            )

            await self._record_execution(step_id, result, trace_id)
            return result

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_result = ToolExecutionResult(
                tool_name=step.tool_name,
                output=str(e),
                is_error=True,
                execution_time_ms=execution_time,
                trace_id=trace_id
            )
            
            logger.error(f"STEP_EXECUTION_FAILED | Step: {step_id} | Error: {str(e)}")
            await self._record_execution(step_id, error_result, trace_id)
            return error_result

    async def _validate_policy(self, step: Any, agent: Any, trace_id: str) -> bool:
        return await agent.policy_engine.check_permission(
            action="execute_tool",
            resource=step.tool_name,
            context={"step_id": step.id, "trace_id": trace_id}
        )

    async def _record_execution(self, step_id: str, result: ToolExecutionResult, trace_id: str):
        await self.publisher.publish_event(
            "execution_traces",
            {
                "step_id": step_id,
                "tool_name": result.tool_name,
                "success": not result.is_error,
                "duration_ms": result.execution_time_ms,
                "trace_id": trace_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )



