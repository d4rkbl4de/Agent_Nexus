import asyncio
import time
from typing import Dict, Any, List, Optional
from uuid import uuid4

from common.messaging.mediator import mediator
from common.messaging.schemas import EventType
from common.config.logging_config import logger
from common.schemas.errors import AppError, ErrorCategory, ErrorCode
from common.ai_sdk.client import AgenticAISDK

from lobes.studyflow.agent_sdk.state import StudyStateManager
from lobes.studyflow.agent_sdk.core.evaluator import KnowledgeEvaluator

class StudyTaskRegistry:
    def __init__(self):
        self._active_tasks: Dict[str, asyncio.Task] = {}
        self._session_locks: Dict[str, asyncio.Lock] = {}
        self.ai_client = AgenticAISDK()

    async def get_active_count(self) -> int:
        return len([t for t in self._active_tasks.values() if not t.done()])

    async def run_knowledge_audit(self, user_id: str, session_id: str, trace_id: str):
        task_id = f"audit_{session_id}_{uuid4().hex[:4]}"
        task = asyncio.create_task(
            self._execute_audit_sequence(user_id, session_id, trace_id)
        )
        self._active_tasks[task_id] = task
        task.add_done_callback(lambda t: self._active_tasks.pop(task_id, None))

    async def _execute_audit_sequence(self, user_id: str, session_id: str, trace_id: str):
        state_manager = StudyStateManager(trace_id=trace_id, user_id=user_id)
        evaluator = KnowledgeEvaluator(trace_id=trace_id, state=state_manager)
        
        async with self._get_lock(session_id):
            try:
                state = await state_manager.get_state()
                if not state.knowledge_gaps:
                    return

                logger.info(f"STARTING_KNOWLEDGE_AUDIT | Session: {session_id}", trace_id=trace_id)
                
                audit_summary = await self.ai_client.chat(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an educational auditor."},
                        {"role": "user", "content": f"Review these knowledge gaps: {json.dumps(state.knowledge_gaps)}. Identify the #1 priority for the next session."}
                    ],
                    trace_id=trace_id
                )

                await mediator.publish(
                    event_type=EventType.DATA_SYNC,
                    payload={
                        "type": "study_audit_complete",
                        "session_id": session_id,
                        "priority_topic": audit_summary
                    },
                    trace_id=trace_id
                )

            except Exception as e:
                logger.error(f"AUDIT_TASK_FAILED | Session: {session_id} | Error: {str(e)}")

    async def cleanup_active_sessions(self):
        for task_id, task in self._active_tasks.items():
            if not task.done():
                task.cancel()
        
        await asyncio.gather(*self._active_tasks.values(), return_exceptions=True)
        self._active_tasks.clear()

    def _get_lock(self, session_id: str) -> asyncio.Lock:
        if session_id not in self._session_locks:
            self._session_locks[session_id] = asyncio.Lock()
        return self._session_locks[session_id]

    async def process_spaced_repetition_queue(self):
        while True:
            try:
                # Logic for scanning vector DB for due cards
                await asyncio.sleep(3600)
            except asyncio.CancelledError:
                break

study_task_registry = StudyTaskRegistry()