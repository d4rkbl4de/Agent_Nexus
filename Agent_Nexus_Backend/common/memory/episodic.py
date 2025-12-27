import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import select, insert
from common.db.session import transactional_session
from common.db.models.episodic_event import EpisodicEvent
from common.config.logging import logger
from common.schemas.errors import AppError, ErrorCategory

class EpisodicMemory:
    def __init__(self, trace_id: str):
        self.trace_id = trace_id

    async def capture_milestone(
        self, 
        content: Any, 
        event_type: str = "milestone", 
        importance: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        event_id = str(uuid.uuid4())
        try:
            async with transactional_session() as session:
                new_event = EpisodicEvent(
                    id=event_id,
                    trace_id=self.trace_id,
                    event_type=event_type,
                    content=content,
                    importance=importance,
                    occurred_at=datetime.utcnow(),
                    metadata_extra=metadata or {}
                )
                session.add(new_event)
            return event_id
        except Exception as e:
            logger.error(f"EPISODIC_CAPTURE_FAILURE | Trace: {self.trace_id} | Error: {str(e)}")
            raise AppError(
                message="Failed to capture episodic milestone",
                category=ErrorCategory.INTERNAL_ERROR,
                status_code=500
            )

    async def get_event_stream(self, limit: int = 20) -> List[Dict[str, Any]]:
        try:
            async with transactional_session() as session:
                stmt = (
                    select(EpisodicEvent)
                    .where(EpisodicEvent.trace_id == self.trace_id)
                    .order_by(EpisodicEvent.occurred_at.desc())
                    .limit(limit)
                )
                result = await session.execute(stmt)
                events = result.scalars().all()
                return [event.to_dict() for event in events]
        except Exception as e:
            logger.error(f"EPISODIC_RETRIEVAL_FAILURE | Trace: {self.trace_id} | Error: {str(e)}")
            return []

    async def get_high_importance_events(self, threshold: float = 0.7) -> List[Dict[str, Any]]:
        try:
            async with transactional_session() as session:
                stmt = (
                    select(EpisodicEvent)
                    .where(
                        EpisodicEvent.trace_id == self.trace_id,
                        EpisodicEvent.importance >= threshold
                    )
                    .order_by(EpisodicEvent.occurred_at.asc())
                )
                result = await session.execute(stmt)
                events = result.scalars().all()
                return [event.to_dict() for event in events]
        except Exception as e:
            logger.error(f"EPISODIC_IMPORTANCE_RETRIEVAL_FAILURE | Trace: {self.trace_id} | Error: {str(e)}")
            return []

    async def delete_trace_history(self) -> bool:
        try:
            async with transactional_session() as session:
                stmt = EpisodicEvent.__table__.delete().where(EpisodicEvent.trace_id == self.trace_id)
                await session.execute(stmt)
            return True
        except Exception as e:
            logger.error(f"EPISODIC_DELETION_FAILURE | Trace: {self.trace_id} | Error: {str(e)}")
            return False