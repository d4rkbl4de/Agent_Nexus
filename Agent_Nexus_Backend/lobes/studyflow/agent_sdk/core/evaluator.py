import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from common.ai_sdk.client import AgenticAISDK
from common.schemas.errors import AppError, ErrorCategory, ErrorCode
from common.config.logging_config import logger
from lobes.studyflow.agent_sdk.state import StudyStateManager

class ComprehensionScore(BaseModel):
    confidence_level: float = Field(ge=0.0, le=1.0)
    understanding_depth: str
    detected_gaps: List[str] = Field(default_factory=list)
    misconceptions: List[str] = Field(default_factory=list)
    next_topic_suggestion: Optional[str] = None
    reasoning: str

class GradingResult(BaseModel):
    is_correct: bool
    score: float = Field(ge=0.0, le=1.0)
    feedback: str
    conceptual_alignment: bool
    remediation_required: bool

class KnowledgeEvaluator:
    def __init__(self, trace_id: str, state: StudyStateManager):
        self.trace_id = trace_id
        self.state = state
        self.ai_client = AgenticAISDK()

    async def evaluate_comprehension(
        self, 
        user_input: str, 
        tutor_response: str, 
        current_topic: str
    ) -> ComprehensionScore:
        try:
            prompt = (
                f"Analyze the student's input: '{user_input}' in the context of the tutor's "
                f"explanation of '{current_topic}'. Tutor said: '{tutor_response}'. "
                "Assess if the student genuinely understands the concept or is just mimicking. "
                "Identify specific knowledge gaps or mental model misconceptions."
            )

            evaluation = await self.ai_client.structured_output(
                model="gpt-4o",
                prompt=prompt,
                response_format=ComprehensionScore,
                trace_id=self.trace_id
            )

            await self.state.update_knowledge_gap(
                topic=current_topic,
                confidence=evaluation.confidence_level,
                misconceptions=evaluation.misconceptions
            )

            return evaluation

        except Exception as e:
            logger.error(f"EVALUATION_CRITICAL_FAILURE | {str(e)}", trace_id=self.trace_id)
            return self._get_default_score()

    async def grade_answer(self, question: str, user_answer: str) -> GradingResult:
        try:
            prompt = (
                f"Question: {question}\n"
                f"Student Answer: {user_answer}\n"
                "Grade this answer for conceptual accuracy. Do not penalize for minor syntax "
                "unless the subject is programming. Focus on the student's reasoning process."
            )

            result = await self.ai_client.structured_output(
                model="gpt-4o-mini",
                prompt=prompt,
                response_format=GradingResult,
                trace_id=self.trace_id
            )

            if result.remediation_required:
                logger.info(f"REMEDIATION_TRIGGERED | Trace: {self.trace_id}", lobe="StudyFlow")

            return result

        except Exception as e:
            logger.error(f"GRADING_FAILURE | {str(e)}", trace_id=self.trace_id)
            raise AppError(
                message="Evaluation engine failed to process the answer.",
                category=ErrorCategory.INTERNAL_ERROR,
                code=ErrorCode.LLM_VALIDATION_FAILED,
                trace_id=self.trace_id
            )

    def _get_default_score(self) -> ComprehensionScore:
        return ComprehensionScore(
            confidence_level=0.5,
            understanding_depth="uncertain",
            reasoning="Fallback score due to evaluation engine timeout."
        )