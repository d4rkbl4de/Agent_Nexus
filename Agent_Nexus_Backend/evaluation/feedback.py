import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from common.config.logging import logger
from common.schemas.errors import AppError, ErrorCategory

class FeedbackSource(BaseModel):
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    system_verifier: bool = False

class FeedbackEntry(BaseModel):
    feedback_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str
    lobe: str
    source: FeedbackSource
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    correction: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class FeedbackEngine:
    def __init__(self, storage_facade: Any):
        self.storage = storage_facade

    async def submit_feedback(self, entry: FeedbackEntry) -> str:
        try:
            await self._persist_feedback(entry)
            
            if entry.correction or entry.rating <= 2:
                await self._trigger_learning_event(entry)
                
            logger.info(f"FEEDBACK_CAPTURED | Trace: {entry.trace_id} | Rating: {entry.rating}")
            return entry.feedback_id
        except Exception as e:
            logger.error(f"FEEDBACK_SUBMISSION_FAILED | Trace: {entry.trace_id} | Error: {str(e)}")
            raise AppError(
                message="Failed to record agent feedback",
                category=ErrorCategory.INTERNAL_ERROR,
                status_code=500
            )

    async def get_agent_feedback_history(
        self, 
        agent_id: str, 
        limit: int = 100
    ) -> List[FeedbackEntry]:
        return await self.storage.query_feedback(agent_id=agent_id, limit=limit)

    async def _persist_feedback(self, entry: FeedbackEntry) -> None:
        await self.storage.save_feedback(entry.model_dump())

    async def _trigger_learning_event(self, entry: FeedbackEntry) -> None:
        learning_payload = {
            "original_trace": entry.trace_id,
            "lobe": entry.lobe,
            "correction": entry.correction,
            "priority": "HIGH" if entry.rating == 1 else "NORMAL"
        }
        await self.storage.queue_for_training(learning_payload)

feedback_engine = None