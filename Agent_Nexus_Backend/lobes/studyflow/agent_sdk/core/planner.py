import json
import uuid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from common.ai_sdk.client import AgenticAISDK
from common.schemas.errors import AppError, ErrorCategory, ErrorCode
from common.config.logging_config import logger
from lobes.studyflow.agent_sdk.registry import StudyAgentDefinition
from lobes.studyflow.agent_sdk.constraints import StudyFlowConstraints

class LearningModule(BaseModel):
    module_id: str
    title: str
    description: str
    estimated_duration_minutes: int
    difficulty: str
    prerequisites: List[str] = Field(default_factory=list)
    learning_objectives: List[str]

class CurriculumPlan(BaseModel):
    plan_id: str
    subject: str
    total_modules: int
    modules: List[LearningModule]
    pedagogical_pathway: str
    recommended_pace: str

class CurriculumPlanner:
    def __init__(
        self,
        definition: StudyAgentDefinition,
        trace_id: str,
        constraints: Optional[StudyFlowConstraints] = None
    ):
        self.definition = definition
        self.trace_id = trace_id
        self.constraints = constraints or StudyFlowConstraints(agent_id=definition.agent_id, trace_id=trace_id)
        self.ai_client = AgenticAISDK()

    async def generate_curriculum(self, subject: str, user_goals: str, duration_days: int = 7) -> CurriculumPlan:
        self.constraints.validate_and_block(user_goals, subject)
        
        try:
            prompt = self._build_curriculum_prompt(subject, user_goals, duration_days)
            
            plan = await self.ai_client.structured_output(
                model="gpt-4o",
                prompt=prompt,
                response_format=CurriculumPlan,
                trace_id=self.trace_id
            )

            self._verify_plan_safety(plan)
            
            logger.info(
                f"CURRICULUM_GENERATED | PlanID: {plan.plan_id} | Subject: {subject}",
                trace_id=self.trace_id,
                lobe="StudyFlow"
            )
            
            return plan

        except Exception as e:
            logger.error(f"CURRICULUM_PLANNING_FAILED | {str(e)}", trace_id=self.trace_id)
            return self._get_emergency_fallback_plan(subject)

    def _build_curriculum_prompt(self, subject: str, goals: str, days: int) -> str:
        return (
            f"You are the Lead Curriculum Architect for {self.definition.name}. "
            f"Subject Expertise: {', '.join(self.definition.subject_expertise)}. "
            f"Pedagogical Style: {self.definition.pedagogical_style}. "
            f"Create a structured {days}-day learning path for: {subject}. "
            f"User's specific goals: {goals}. "
            "Ensure the plan flows logically from foundational concepts to advanced application. "
            "Each module must have clear learning objectives."
        )

    def _verify_plan_safety(self, plan: CurriculumPlan):
        if len(plan.modules) > 15:
            raise AppError(
                message="Generated curriculum exceeds maximum complexity limits.",
                category=ErrorCategory.POLICY_VIOLATION,
                code=ErrorCode.BAD_REQUEST,
                trace_id=self.trace_id
            )
        
        for module in plan.modules:
            if any(p in module.title.lower() for p in self.constraints.prohibited_topics):
                raise AppError(
                    message=f"Curriculum contains restricted content in module: {module.title}",
                    category=ErrorCategory.POLICY_VIOLATION,
                    code=ErrorCode.FORBIDDEN,
                    trace_id=self.trace_id
                )

    def _get_emergency_fallback_plan(self, subject: str) -> CurriculumPlan:
        return CurriculumPlan(
            plan_id=f"fallback_{uuid.uuid4().hex[:8]}",
            subject=subject,
            total_modules=1,
            modules=[
                LearningModule(
                    module_id="m_intro_001",
                    title=f"Introduction to {subject}",
                    description="A foundational overview of the requested topic.",
                    estimated_duration_minutes=45,
                    difficulty="beginner",
                    learning_objectives=["Understand core concepts", "Identify key terminology"]
                )
            ],
            pedagogical_pathway="Linear/Foundational",
            recommended_pace="Standard"
        )

    async def adapt_plan(self, current_plan: CurriculumPlan, knowledge_gaps: List[str]) -> CurriculumPlan:
        prompt = (
            f"The student is struggling with: {', '.join(knowledge_gaps)}. "
            f"Modify the following curriculum plan to include remediation modules for these topics "
            f"without removing the original core objectives: {current_plan.model_dump_json()}"
        )
        
        adapted_plan = await self.ai_client.structured_output(
            model="gpt-4o",
            prompt=prompt,
            response_format=CurriculumPlan,
            trace_id=self.trace_id
        )
        
        return adapted_plan