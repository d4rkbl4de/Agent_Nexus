import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

from common.config.logging import logger
from common.schemas.errors import AppError, ErrorCategory
from lobes.chatbuddy.agent_sdk.state import chat_state_manager
from common.messaging.publisher import MessagePublisher

class ChatMemorySyncService:
    def __init__(self):
        self.publisher = MessagePublisher()
        self._sync_interval = 30
        self._active_sync_tasks: Dict[str, asyncio.Task] = {}

    async def sync_session_to_long_term(
        self, 
        session_id: str, 
        trace_id: str, 
        force: bool = False
    ) -> bool:
        logger.info(f"MEMORY_SYNC_START | Session: {session_id} | Trace: {trace_id}")
        
        try:
            state = chat_state_manager.get_state(session_id)
            
            if not force and len(state.history) < 2:
                logger.debug(f"MEMORY_SYNC_SKIPPED | Session: {session_id} | Reason: Insufficient history")
                return False

            sync_payload = {
                "session_id": session_id,
                "agent_id": state.agent_id,
                "trace_id": trace_id,
                "lobe": "chatbuddy",
                "memory_type": "EPISODIC",
                "content": state.history,
                "metadata": state.values,
                "timestamp": datetime.utcnow().isoformat()
            }

            await self.publisher.publish_event(
                topic="memory.write.request",
                payload=sync_payload
            )

            chat_state_manager.update_value(
                session_id=session_id,
                key="last_synced_at",
                value=datetime.utcnow().isoformat(),
                trace_id=trace_id
            )

            logger.info(f"MEMORY_SYNC_DISPATCHED | Session: {session_id} | Trace: {trace_id}")
            return True

        except Exception as e:
            logger.error(f"MEMORY_SYNC_FAILURE | Session: {session_id} | Error: {str(e)}")
            return False

    async def start_periodic_sync(self, session_id: str, trace_id: str):
        if session_id in self._active_sync_tasks:
            return

        task = asyncio.create_task(self._sync_loop(session_id, trace_id))
        self._active_sync_tasks[session_id] = task
        logger.info(f"PERIODIC_SYNC_ENABLED | Session: {session_id}")

    async def _sync_loop(self, session_id: str, trace_id: str):
        try:
            while True:
                await asyncio.sleep(self._sync_interval)
                await self.sync_session_to_long_term(session_id, trace_id)
        except asyncio.CancelledError:
            logger.info(f"PERIODIC_SYNC_STOPPED | Session: {session_id}")
        except Exception as e:
            logger.error(f"PERIODIC_SYNC_CRASH | Session: {session_id} | Error: {str(e)}")

    async def stop_sync(self, session_id: str):
        task = self._active_sync_tasks.pop(session_id, None)
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    async def consolidate_on_shutdown(self, session_id: str, trace_id: str):
        await self.stop_sync(session_id)
        await self.sync_session_to_long_term(session_id, trace_id, force=True)

memory_sync_service = ChatMemorySyncService()