import asyncio
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

from common.config.logging import logger
from common.schemas.errors import AppError
from lobes.autoagent_hub.orchestration.planner import OrchestrationPlanner
from lobes.autoagent_hub.orchestration.executor import OrchestrationExecutor
from lobes.autoagent_hub.orchestration.supervisor import OrchestrationSupervisor
from lobes.autoagent_hub.agent_sdk.registry import HubAgentRegistry

class HubCoordinator:
    def __init__(self):
        self.registry = HubAgentRegistry()
        self.planner = OrchestrationPlanner()
        self.executor = OrchestrationExecutor()
        self.supervisor = OrchestrationSupervisor()
        self._active_sessions: Dict[str, Dict[str, Any]] = {}

    async def coordinate_mission(
        self, 
        goal: str, 
        context: Dict[str, Any], 
        agent_id: str, 
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        trace_id = trace_id or str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        
        logger.info(f"MISSION_COORDINATION_START | Session: {session_id} | Agent: {agent_id} | Trace: {trace_id}")

        try:
            agent = await self.registry.get_agent(agent_id)
            if not agent:
                raise AppError.agent_failure("Target agent not found in Hub registry", trace_id, agent_id)

            plan = await self.planner.create_plan(
                goal=goal,
                context=context,
                agent=agent,
                trace_id=trace_id
            )

            self._active_sessions[session_id] = {
                "plan": plan,
                "agent": agent,
                "results": [],
                "status": "EXECUTING",
                "started_at": datetime.utcnow().isoformat()
            }

            for step in plan.steps:
                execution_result = await self.executor.execute_step(
                    step=step,
                    agent=agent,
                    trace_id=trace_id
                )

                supervision_outcome = await self.supervisor.supervise_execution(
                    plan=plan,
                    current_step=step,
                    result=execution_result,
                    agent=agent,
                    trace_id=trace_id
                )

                action = supervision_outcome.get("action")

                if action == "CONTINUE":
                    self._active_sessions[session_id]["results"].append(execution_result)
                    continue
                
                if action == "RETRY_STEP":
                    updated_step = supervision_outcome.get("updated_step", step)
                    retry_result = await self.executor.execute_step(updated_step, agent, trace_id)
                    self._active_sessions[session_id]["results"].append(retry_result)
                    if retry_result.is_error:
                        break
                    continue

                if action == "ESCALATE" or action == "ABORT":
                    logger.error(f"MISSION_HALTED | Session: {session_id} | Reason: {supervision_outcome.get('reason')}")
                    self._active_sessions[session_id]["status"] = "FAILED"
                    return {
                        "session_id": session_id,
                        "status": "FAILED",
                        "trace_id": trace_id,
                        "reason": supervision_outcome.get("reason")
                    }

            self._active_sessions[session_id]["status"] = "COMPLETED"
            return {
                "session_id": session_id,
                "status": "COMPLETED",
                "trace_id": trace_id,
                "results": self._active_sessions[session_id]["results"]
            }

        except Exception as e:
            logger.critical(f"COORDINATION_CRITICAL_FAILURE | Session: {session_id} | Error: {str(e)}")
            if session_id in self._active_sessions:
                self._active_sessions[session_id]["status"] = "CRASHED"
            raise
        finally:
            await self._cleanup_session(session_id)

    async def _cleanup_session(self, session_id: str):
        if session_id in self._active_sessions:

            await asyncio.sleep(0.1) 

    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        return self._active_sessions.get(session_id)