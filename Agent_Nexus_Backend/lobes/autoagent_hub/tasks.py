import asyncio
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import ValidationError

from common.config.logging import logger
from common.messaging.publisher import MessagePublisher
from common.schemas.internal import ToolExecutionCall, ToolExecutionResult
from common.schemas.errors import AppError, ErrorCategory
from lobes.autoagent_hub.agent_sdk.registry import HubAgentRegistry
from lobes.autoagent_hub.orchestration.planner import OrchestrationPlanner
from lobes.autoagent_hub.orchestration.executor import OrchestrationExecutor

class HubTaskProcessor:
    def __init__(self):
        self.registry = HubAgentRegistry()
        self.planner = OrchestrationPlanner()
        self.executor = OrchestrationExecutor()
        self.publisher = MessagePublisher()

    async def process_hub_task(self, task_data: Dict[str, Any], trace_id: Optional[str] = None):
        trace_id = trace_id or str(uuid.uuid4())
        task_id = task_data.get("task_id", str(uuid.uuid4()))
        
        logger.info(f"TASK_EXECUTION_START | Task: {task_id} | Trace: {trace_id}")

        try:
            agent_id = task_data.get("agent_id")
            if not agent_id:
                raise ValueError("MISSING_AGENT_ID")

            agent = await self.registry.get_agent(agent_id)
            if not agent:
                raise AppError.agent_failure("Agent not found in registry", trace_id, agent_id)

            plan = await self.planner.create_plan(
                goal=task_data.get("goal"),
                context=task_data.get("context", {}),
                agent=agent,
                trace_id=trace_id
            )

            results = []
            for step in plan.steps:
                if step.requires_approval and not task_data.get("pre_approved"):
                    await self._handle_approval_required(task_id, step, trace_id)
                    return {"status": "AWAITING_APPROVAL", "task_id": task_id}

                step_result = await self.executor.execute_step(
                    step=step,
                    agent=agent,
                    trace_id=trace_id
                )
                results.append(step_result)

                if step_result.is_error and not step.continue_on_failure:
                    break

            await self._finalize_task(task_id, results, trace_id)
            return {"status": "COMPLETED", "task_id": task_id, "results": results}

        except Exception as e:
            await self._handle_task_failure(task_id, e, trace_id)
            return {"status": "FAILED", "task_id": task_id, "error": str(e)}

    async def _handle_approval_required(self, task_id: str, step: Any, trace_id: str):
        await self.publisher.publish_event(
            "agent_events",
            {
                "type": "APPROVAL_REQUIRED",
                "task_id": task_id,
                "step_id": step.id,
                "trace_id": trace_id
            }
        )
        logger.warning(f"TASK_SUSPENDED_FOR_APPROVAL | Task: {task_id} | Step: {step.id}")

    async def _finalize_task(self, task_id: str, results: List[Any], trace_id: str):
        await self.publisher.publish_event(
            "task_results",
            {
                "task_id": task_id,
                "status": "SUCCESS",
                "completed_at": datetime.utcnow().isoformat(),
                "trace_id": trace_id
            }
        )
        logger.info(f"TASK_EXECUTION_COMPLETE | Task: {task_id}")

    async def _handle_task_failure(self, task_id: str, error: Exception, trace_id: str):
        logger.error(f"TASK_EXECUTION_FAILED | Task: {task_id} | Error: {str(error)}")
        await self.publisher.publish_event(
            "task_results",
            {
                "task_id": task_id,
                "status": "FAILED",
                "error": str(error),
                "trace_id": trace_id
            }
        )

processor = HubTaskProcessor()

async def start_worker():
    import nats
    nc = await nats.connect(os.getenv("NATS_URL", "nats://localhost:4222"))
    js = nc.jetstream()
    
    sub = await js.subscribe("hub.tasks", durable="hub-worker")
    
    while True:
        try:
            msg = await sub.next_msg()
            data = msg.data.decode()
            await processor.process_hub_task(data)
            await msg.ack()
        except Exception as e:
            logger.error(f"WORKER_LOOP_ERROR | {str(e)}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(start_worker())