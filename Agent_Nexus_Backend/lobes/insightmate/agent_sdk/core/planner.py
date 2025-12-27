import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from common.ai_sdk.client import AgenticAISDK
from common.schemas.errors import AppError, ErrorCategory, ErrorCode
from common.config.logging_config import logger
from lobes.insightmate.agent_sdk.registry import InsightAgentDefinition
from lobes.insightmate.agent_sdk.core.verifier import PolicyVerifier

class AnalysisStep(BaseModel):
    step_id: str
    task_id: str
    priority: int
    dependencies: List[str] = Field(default_factory=list)
    description: str

class AnalysisPlan(BaseModel):
    plan_id: str
    steps: List[AnalysisStep]
    estimated_tokens: int
    reasoning_path: str

class InsightPlanner:
    def __init__(
        self,
        definition: InsightAgentDefinition,
        trace_id: str,
        verifier: Optional[PolicyVerifier] = None
    ):
        self.definition = definition
        self.trace_id = trace_id
        self.verifier = verifier
        self.ai_client = AgenticAISDK()

    async def create_plan(self, transcript_metadata: Dict[str, Any]) -> AnalysisPlan:
        try:
            prompt = self._build_planning_prompt(transcript_metadata)
            
            plan_data = await self.ai_client.structured_output(
                model="gpt-4o",
                prompt=prompt,
                response_format=AnalysisPlan,
                trace_id=self.trace_id
            )

            self._validate_plan_against_capabilities(plan_data)
            
            logger.info(
                f"INSIGHT_PLAN_GENERATED | Steps: {len(plan_data.steps)}",
                trace_id=self.trace_id,
                extra={"plan_id": plan_data.plan_id}
            )
            
            return plan_data

        except Exception as e:
            logger.error(f"PLANNING_FAILURE | Trace: {self.trace_id} | Error: {str(e)}")
            return self._generate_fallback_plan()

    def _build_planning_prompt(self, metadata: Dict[str, Any]) -> str:
        available_tasks = ", ".join(self.definition.supported_tasks)
        return (
            f"You are the Planning Brain for {self.definition.name}. "
            f"Based on a meeting transcript with metadata: {json.dumps(metadata)}, "
            "create an optimized execution plan to extract maximum value. "
            f"You MUST only use these supported tasks: [{available_tasks}]. "
            "Sequence them logically (e.g., summarize before detecting sentiment)."
        )

    def _validate_plan_against_capabilities(self, plan: AnalysisPlan):
        for step in plan.steps:
            if step.task_id not in self.definition.supported_tasks:
                raise AppError(
                    message=f"Plan requested unsupported task: {step.task_id}",
                    category=ErrorCategory.POLICY_VIOLATION,
                    code=ErrorCode.BAD_REQUEST,
                    trace_id=self.trace_id
                )

    def _generate_fallback_plan(self) -> AnalysisPlan:
        steps = [
            AnalysisStep(
                step_id="step_1",
                task_id="generate_meeting_summary",
                priority=1,
                description="Default summary extraction"
            ),
            AnalysisStep(
                step_id="step_2",
                task_id="extract_action_items",
                priority=2,
                dependencies=["step_1"],
                description="Default action item extraction"
            )
        ]
        return AnalysisPlan(
            plan_id=f"fallback_{self.trace_id}",
            steps=steps,
            estimated_tokens=4000,
            reasoning_path="Fallback plan triggered due to planning engine failure."
        )

    async def decompose_transcript(self, transcript: str, max_chunk_size: int = 10000) -> List[str]:
        words = transcript.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            if current_length + len(word) > max_chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks