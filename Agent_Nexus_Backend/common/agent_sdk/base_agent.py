import abc
import uuid
import time
import traceback
from typing import Any, Dict, List, Optional, Type, Union
from pydantic import BaseModel, Field, ValidationError

from common.config.logging import logger
from common.agent_sdk.orchestration_state import OrchestrationState
from common.agent_sdk.lifecycle import AgentLifecycle
from common.agent_sdk.planner import Planner
from common.agent_sdk.executor import Executor
from common.agent_sdk.verifier import Verifier
from tracing.context import get_trace_id, get_agent_id
from policy.execution_policy import execution_guard

class AgentMetadata(BaseModel):
    agent_id: str = Field(..., description="Unique identifier for the lobe")
    version: str = Field("1.0.0", pattern=r"^\d+\.\d+\.\d+$")
    capabilities: List[str] = Field(default_factory=list)
    max_iterations: int = Field(default=10, ge=1, le=50)
    timeout_seconds: int = Field(default=300, gt=0)

class AgentResult(BaseModel):
    status: str
    trace_id: str
    agent_id: str
    output: Any
    metrics: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None

class BaseAgent(abc.ABC):
    def __init__(self, metadata: AgentMetadata):
        self.metadata = metadata
        self.lifecycle = AgentLifecycle()
        self.state = OrchestrationState()
        self.planner = Planner()
        self.executor = Executor()
        self.verifier = Verifier()

    @abc.abstractmethod
    async def initialize_tools(self) -> None:
        pass

    @abc.abstractmethod
    async def get_system_prompt(self) -> str:
        pass

    @execution_guard(max_depth=20)
    async def run(self, task: str, input_context: Optional[Dict[str, Any]] = None) -> AgentResult:
        start_time = time.perf_counter()
        trace_id = get_trace_id() or f"gen-{uuid.uuid4().hex[:8]}"
        input_context = input_context or {}
        
        logger.info(
            f"AGENT_EXECUTION_START | Lobe: {self.metadata.agent_id} | "
            f"Trace: {trace_id} | Task_Len: {len(task)}"
        )

        try:
            await self.initialize_tools()
            await self.lifecycle.on_bootstrap(self.metadata, trace_id)

            plan = await self.planner.create_plan(
                goal=task, 
                context=input_context,
                capabilities=self.metadata.capabilities
            )
            
            self.state.update_plan(plan)
            logger.info(f"PLAN_ACQUIRED | Trace: {trace_id} | Steps: {len(plan.steps)}")

            for step_idx, step in enumerate(plan.steps):
                if step_idx >= self.metadata.max_iterations:
                    logger.warning(f"ITERATION_CAP_HIT | Trace: {trace_id} | Limit: {self.metadata.max_iterations}")
                    break

                logger.debug(f"STEP_EXECUTION | Trace: {trace_id} | Step: {step_idx} | Action: {step.action}")
                
                step_result = await self.executor.execute(step, self.state)
                
                verification = await self.verifier.verify_step(
                    step=step, 
                    result=step_result, 
                    context=self.state.get_full_context()
                )

                if not verification.is_valid:
                    logger.error(
                        f"STEP_VERIFICATION_FAILURE | Trace: {trace_id} | "
                        f"Step: {step_idx} | Reason: {verification.reason}"
                    )
                    if verification.should_retry:
                        # Logic for internal agent retry loop or re-planning
                        pass

                self.state.add_step_result(step_idx, step_result, verification)

            final_output = await self.planner.synthesize_final_answer(self.state)
            
            execution_time = time.perf_counter() - start_time
            result = AgentResult(
                status="success",
                trace_id=trace_id,
                agent_id=self.metadata.agent_id,
                output=final_output,
                metrics={
                    "execution_time_ms": execution_time * 1000,
                    "steps_completed": len(self.state.history)
                }
            )

            await self.lifecycle.on_success(self.metadata, result)
            return result

        except Exception as e:
            execution_time = time.perf_counter() - start_time
            error_msg = f"{type(e).__name__}: {str(e)}"
            
            logger.critical(
                f"AGENT_RUNTIME_FATAL | Trace: {trace_id} | Error: {error_msg}\n"
                f"{traceback.format_exc()}"
            )
            
            failure_result = AgentResult(
                status="failed",
                trace_id=trace_id,
                agent_id=self.metadata.agent_id,
                output=None,
                error=error_msg,
                metrics={"execution_time_ms": execution_time * 1000}
            )
            
            await self.lifecycle.on_failure(self.metadata, failure_result)
            return failure_result