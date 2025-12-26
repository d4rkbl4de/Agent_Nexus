import uuid
import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from common.config.logging import logger
from common.llm.client import LLMClient
from common.agent_sdk.orchestration_state import OrchestrationState
from tracing.context import get_trace_id

class PlanStep(BaseModel):
    step_id: int
    action: str
    input_params: Dict[str, Any]
    verification_criteria: Dict[str, Any]
    depends_on: List[int] = Field(default_factory=list)

class ExecutionPlan(BaseModel):
    plan_id: str
    goal: str
    steps: List[PlanStep]
    estimated_tokens: int

class Planner:
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client
        self.system_prompt = (
            "You are the Strategic Planner for the Agent Nexus Hive Mind. "
            "Decompose the user goal into atomic, verifiable steps."
        )

    async def create_plan(
        self, 
        goal: str, 
        context: Dict[str, Any], 
        capabilities: List[str]
    ) -> ExecutionPlan:
        trace_id = get_trace_id()
        logger.info(f"PLANNING_PHASE_START | Trace: {trace_id} | Goal: {goal[:50]}")

        try:
            mock_plan = ExecutionPlan(
                plan_id=str(uuid.uuid4()),
                goal=goal,
                steps=[
                    PlanStep(
                        step_id=1,
                        action="search_memory",
                        input_params={"query": goal},
                        verification_criteria={"min_results": 1}
                    )
                ],
                estimated_tokens=500
            )
            return mock_plan
            
        except Exception as e:
            logger.error(f"PLANNING_CRITICAL_FAILURE | Trace: {trace_id} | Error: {str(e)}")
            raise e

    async def synthesize_final_answer(self, state: OrchestrationState) -> Any:
        history = state.get_history()
        logger.info(f"SYNTHESIS_PHASE | History_Steps: {len(history)}")
        return history[-1].output if history else "No steps completed."