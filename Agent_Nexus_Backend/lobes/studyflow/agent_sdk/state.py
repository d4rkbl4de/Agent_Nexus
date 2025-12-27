import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from common.memory.short_term import ShortTermMemory
from common.config.logging_config import logger
from common.schemas.errors import AppError, ErrorCategory, ErrorCode

class KnowledgeGap(BaseModel):
    topic: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    last_assessed: datetime = Field(default_factory=datetime.utcnow)
    misconceptions: List[str] = Field(default_factory=list)
    remediation_status: str = "pending"

class StudySessionState(BaseModel):
    session_id: str
    user_id: str
    agent_id: str
    subject: str
    difficulty_level: str
    current_module: Optional[str] = None
    curriculum_path: List[str] = Field(default_factory=list)
    completed_topics: List[str] = Field(default_factory=list)
    knowledge_gaps: Dict[str, KnowledgeGap] = Field(default_factory=dict)
    active_recall_history: List[Dict[str, Any]] = Field(default_factory=list)
    total_tokens_consumed: int = 0
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class StudyStateManager:
    def __init__(self, trace_id: str, user_id: str):
        self.trace_id = trace_id
        self.user_id = user_id
        self.stm = ShortTermMemory(trace_id=trace_id, ttl=3600)
        self.state_key = f"study_state_{user_id}_{trace_id}"

    async def initialize_session(self, session_id: str, agent_id: str, subject: str, difficulty: str):
        state = StudySessionState(
            session_id=session_id,
            user_id=self.user_id,
            agent_id=agent_id,
            subject=subject,
            difficulty_level=difficulty
        )
        await self.save_state(state)

    async def get_state(self) -> StudySessionState:
        data = await self.stm.get(self.state_key)
        if not data:
            raise AppError(
                message="Study session state not found or has expired",
                category=ErrorCategory.NOT_FOUND_ERROR,
                code=ErrorCode.RESOURCE_NOT_FOUND,
                trace_id=self.trace_id
            )
        return StudySessionState(**data)

    async def save_state(self, state: StudySessionState):
        state.updated_at = datetime.utcnow()
        success = await self.stm.set(self.state_key, state.model_dump())
        if not success:
            logger.error(f"STUDY_STATE_SAVE_FAILED | User: {self.user_id} | Trace: {self.trace_id}")
            raise AppError(
                message="Failed to persist study session state",
                category=ErrorCategory.INTERNAL_ERROR,
                code=ErrorCode.SYSTEM_PANIC,
                trace_id=self.trace_id
            )

    async def update_knowledge_gap(self, topic: str, confidence: float, misconceptions: List[str] = None):
        state = await self.get_state()
        gap = state.knowledge_gaps.get(topic, KnowledgeGap(topic=topic, confidence_score=confidence))
        gap.confidence_score = confidence
        gap.last_assessed = datetime.utcnow()
        if misconceptions:
            gap.misconceptions = list(set(gap.misconceptions + misconceptions))
        
        state.knowledge_gaps[topic] = gap
        if confidence > 0.8 and topic not in state.completed_topics:
            state.completed_topics.append(topic)
            gap.remediation_status = "resolved"
            
        await self.save_state(state)

    async def log_active_recall(self, question: str, user_answer: str, is_correct: bool, feedback: str):
        state = await self.get_state()
        state.active_recall_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "question": question,
            "correct": is_correct,
            "feedback_given": feedback
        })
        await self.save_state(state)

    async def set_curriculum(self, topics: List[str]):
        state = await self.get_state()
        state.curriculum_path = topics
        await self.save_state(state)

    async def sync_token_usage(self, tokens: int):
        state = await self.get_state()
        state.total_tokens_consumed += tokens
        await self.save_state(state)

    async def clear_session(self):
        await self.stm.delete(self.state_key)
        logger.info(f"STUDY_STATE_CLEARED | User: {self.user_id}", lobe="StudyFlow")