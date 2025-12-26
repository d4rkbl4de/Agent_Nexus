import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

from common.config.logging import logger
from common.schemas.internal import ToolExecutionResult
from common.schemas.errors import AppError, ErrorCategory
from common.messaging.publisher import MessagePublisher
from lobes.autoagent_hub.orchestration.planner import AgentPlan, PlanStep

class OrchestrationSupervisor:
    def __init__(self):
        self.publisher = MessagePublisher()
        self.max_corrections = 3

    async def supervise_execution(
        self,
        plan: AgentPlan,
        current_step: PlanStep,
        result: ToolExecutionResult,
        agent: Any,
        trace_id: str
    ) -> Dict[str, Any]:
        logger.info(f"SUPERVISION_START | Plan: {plan.plan_id} | Step: {current_step.id} | Trace: {trace_id}")

        if not result.is_error:
            quality_check = await self._evaluate_result_quality(result, current_step, agent, trace_id)
            if quality_check.get("passed"):
                return {"action": "CONTINUE", "next_step_index": plan.steps.index(current_step) + 1}
            
            return await self._handle_subpar_quality(plan, current_step, quality_check, agent, trace_id)

        return await self._handle_execution_failure(plan, current_step, result, agent, trace_id)

    async def _evaluate_result_quality(
        self, 
        result: ToolExecutionResult, 
        step: PlanStep, 
        agent: Any, 
        trace_id: str
    ) -> Dict[str, Any]:
        evaluation = await agent.reason(
            instruction="Evaluate the following tool output against the intended step description. Return a JSON with 'passed' (bool) and 'reason' (string).",
            context={
                "step_description": step.description,
                "tool_output": result.output,
                "tool_name": result.tool_name
            },
            trace_id=trace_id
        )
        return evaluation

    async def _handle_subpar_quality(
        self,
        plan: AgentPlan,
        step: PlanStep,
        evaluation: Dict[str, Any],
        agent: Any,
        trace_id: str
    ) -> Dict[str, Any]:
        correction_count = plan.metadata.get("corrections", {}).get(step.id, 0)
        
        if correction_count >= self.max_corrections:
            logger.error(f"MAX_CORRECTIONS_REACHED | Step: {step.id}")
            return {"action": "ESCALATE", "reason": "Quality threshold not met after multiple attempts"}

        plan.metadata.setdefault("corrections", {})[step.id] = correction_count + 1
        
        replan = await agent.reason(
            instruction=f"The previous attempt failed quality checks. Reason: {evaluation.get('reason')}. Provide corrected arguments for the tool.",
            context={"previous_args": step.args, "error": evaluation.get("reason")},
            trace_id=trace_id
        )
        
        step.args = replan.get("corrected_args", step.args)
        return {"action": "RETRY_STEP", "updated_step": step}

    async def _handle_execution_failure(
        self,
        plan: AgentPlan,
        step: PlanStep,
        result: ToolExecutionResult,
        agent: Any,
        trace_id: str
    ) -> Dict[str, Any]:
        if step.continue_on_failure:
            logger.warning(f"FAILURE_IGNORED_BY_POLICY | Step: {step.id}")
            return {"action": "CONTINUE", "next_step_index": plan.steps.index(step) + 1}

        recovery_strategy = await agent.reason(
            instruction="A tool execution failed. Determine if we should 'RETRY', 'REPLAN', or 'ABORT'.",
            context={"tool": result.tool_name, "error": result.output},
            trace_id=trace_id
        )

        action = recovery_strategy.get("action", "ABORT")
        
        await self.publisher.publish_event(
            "supervision_events",
            {
                "plan_id": plan.plan_id,
                "step_id": step.id,
                "event": "RECOVERY_TRIGGERED",
                "action": action,
                "trace_id": trace_id
            }
        )

        return {"action": action, "details": recovery_strategy}