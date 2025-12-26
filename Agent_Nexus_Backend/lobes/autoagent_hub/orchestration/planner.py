import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from common.config.logging import logger
from common.schemas.errors import AppError
from common.schemas.internal import ToolDefinition
from lobes.autoagent_hub.agent_sdk.policies import PolicyEngine

class PlanStep(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tool_name: str
    args: Dict[str, Any]
    requires_approval: bool = False
    continue_on_failure: bool = False
    description: str

class AgentPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    goal: str
    steps: List[PlanStep]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class OrchestrationPlanner:
    def __init__(self):
        self.policy_engine = PolicyEngine()

    async def create_plan(
        self, 
        goal: str, 
        context: Dict[str, Any], 
        agent: Any, 
        trace_id: str
    ) -> AgentPlan:
        logger.info(f"PLANNING_START | Agent: {agent.id} | Goal: {goal} | Trace: {trace_id}")
        
        try:
            available_tools = await agent.get_available_tools()
            
            raw_plan = await agent.reason(
                instruction=f"Create a step-by-step plan to achieve: {goal}",
                context=context,
                tools=available_tools,
                trace_id=trace_id
            )

            validated_steps = []
            for step_data in raw_plan.get("steps", []):
                step = PlanStep(
                    tool_name=step_data["tool"],
                    args=step_data.get("args", {}),
                    requires_approval=self._determine_approval_need(step_data, agent),
                    continue_on_failure=step_data.get("optional", False),
                    description=step_data.get("thought", "Executing reasoning step")
                )
                
                if await self._verify_step_safety(step, agent, trace_id):
                    validated_steps.append(step)
                else:
                    logger.warning(f"PLAN_STEP_REJECTED | Tool: {step.tool_name} | Reason: Policy Violation")

            if not validated_steps:
                raise AppError.policy_violation(
                    message="Planner failed to generate any safe executable steps.",
                    trace_id=trace_id,
                    policy_name="PlanSafetyValidator"
                )

            plan = AgentPlan(
                goal=goal,
                steps=validated_steps,
                metadata={"agent_version": agent.version, "trace_id": trace_id}
            )

            logger.info(f"PLANNING_SUCCESS | PlanID: {plan.plan_id} | Steps: {len(plan.steps)}")
            return plan

        except Exception as e:
            logger.error(f"PLANNING_CRITICAL_FAILURE | Trace: {trace_id} | Error: {str(e)}")
            raise

    def _determine_approval_need(self, step_data: Dict[str, Any], agent: Any) -> bool:
        sensitive_tools = {"delete_resource", "transfer_funds", "modify_system_config", "send_external_email"}
        return step_data["tool"] in sensitive_tools or agent.config.get("force_approval", False)

    async def _verify_step_safety(self, step: PlanStep, agent: Any, trace_id: str) -> bool:
        return await self.policy_engine.check_permission(
            action="plan_step",
            resource=step.tool_name,
            context={"args": step.args, "agent_id": agent.id, "trace_id": trace_id}
        )