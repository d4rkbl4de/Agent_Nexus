import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from common.ai_sdk.client import AgenticAISDK
from common.schemas.errors import AppError, ErrorCategory, ErrorCode
from common.config.logging_config import logger
from lobes.studyflow.agent_sdk.state import StudyStateManager
from lobes.studyflow.agent_sdk.core.evaluator import KnowledgeEvaluator
from lobes.studyflow.agent_sdk.constraints import StudyFlowConstraints

class AdaptiveTutor:
    def __init__(
        self,
        state: StudyStateManager,
        trace_id: str,
        evaluator: KnowledgeEvaluator,
        constraints: StudyFlowConstraints
    ):
        self.state = state
        self.trace_id = trace_id
        self.evaluator = evaluator
        self.constraints = constraints
        self.ai_client = AgenticAISDK()

    async def generate_response(self, user_input: str) -> Dict[str, Any]:
        start_time = datetime.utcnow().timestamp()
        current_state = await self.state.get_state()
        
        self.constraints.validate_and_block(user_input, current_state.subject)
        self.constraints.check_runtime_compliance(start_time)

        context_data = self._build_pedagogical_context(current_state)
        
        try:
            response = await self.ai_client.chat(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": context_data["system_prompt"]},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.4,
                trace_id=self.trace_id
            )

            evaluation = await self.evaluator.evaluate_comprehension(
                user_input=user_input,
                tutor_response=response,
                current_topic=current_state.current_module or "General"
            )

            await self.state.sync_token_usage(len(response.split()) * 1.3)
            
            return {
                "tutor_message": response,
                "evaluation": evaluation.model_dump(),
                "session_id": current_state.session_id,
                "suggested_next_topic": evaluation.next_topic_suggestion
            }

        except Exception as e:
            logger.error(f"TUTOR_RESPONSE_FAILURE | Trace: {self.trace_id} | Error: {str(e)}")
            raise

    def _build_pedagogical_context(self, state: Any) -> Dict[str, str]:
        gaps = [g.topic for g in state.knowledge_gaps.values() if g.confidence_score < 0.5]
        
        system_prompt = (
            f"You are an adaptive AI Tutor specializing in {state.subject}. "
            f"Current Student Level: {state.difficulty_level}. "
            f"Knowledge Gaps to Address: {', '.join(gaps)}. "
            "Instructional Strategy: Use the Socratic method. Guide the student with questions "
            "rather than giving direct answers. If the student is struggling, break the concept "
            "into smaller, atomic parts."
        )
        
        return {"system_prompt": system_prompt}

    async def conduct_active_recall(self) -> Dict[str, Any]:
        state = await self.state.get_state()
        
        if not state.completed_topics:
            return {"message": "Not enough material covered yet for active recall."}

        target_topic = state.completed_topics[-1]
        
        question = await self.ai_client.chat(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"Generate a challenging conceptual question about {target_topic}."},
                {"role": "user", "content": "The question should test deep understanding, not rote memorization."}
            ],
            trace_id=self.trace_id
        )

        return {
            "type": "active_recall",
            "topic": target_topic,
            "question": question
        }

    async def process_feedback(self, question: str, user_answer: str):
        eval_result = await self.evaluator.grade_answer(question, user_answer)
        
        await self.state.log_active_recall(
            question=question,
            user_answer=user_answer,
            is_correct=eval_result["is_correct"],
            feedback=eval_result["feedback"]
        )
        
        return eval_result