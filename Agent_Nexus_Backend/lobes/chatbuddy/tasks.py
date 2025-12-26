import uuid
import asyncio
from typing import Any, Dict, Optional
from datetime import datetime

from common.config.logging import logger
from common.schemas.errors import AppError, ErrorCategory
from common.messaging.publisher import MessagePublisher
from lobes.chatbuddy.agent_sdk.core.coordinator import ChatCoordinator
from lobes.chatbuddy.agent_sdk.state import chat_state_manager

class ChatTaskProcessor:
    def __init__(self):
        self.coordinator = ChatCoordinator()
        self.publisher = MessagePublisher()

    async def process_chat_interaction(
        self, 
        task_data: Dict[str, Any], 
        trace_id: str
    ) -> None:
        task_id = task_data.get("task_id", str(uuid.uuid4()))
        user_id = task_data.get("user_id")
        session_id = task_data.get("session_id")
        message_content = task_data.get("message")

        logger.info(f"CHAT_TASK_START | Task: {task_id} | Session: {session_id} | Trace: {trace_id}")

        try:
            chat_state_manager.append_history(session_id, {
                "role": "user",
                "content": message_content,
                "trace_id": trace_id,
                "timestamp": datetime.utcnow().isoformat()
            })

            response = await self.coordinator.execute_chat_turn(
                session_id=session_id,
                message=message_content,
                trace_id=trace_id
            )

            chat_state_manager.append_history(session_id, {
                "role": "assistant",
                "content": response.get("content"),
                "trace_id": trace_id,
                "timestamp": datetime.utcnow().isoformat()
            })

            await self.publisher.publish_event(
                topic=f"chatbuddy.events.{session_id}.completed",
                payload={
                    "task_id": task_id,
                    "session_id": session_id,
                    "user_id": user_id,
                    "response": response,
                    "status": "SUCCESS",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

            logger.info(f"CHAT_TASK_SUCCESS | Task: {task_id} | Trace: {trace_id}")

        except Exception as e:
            logger.error(f"CHAT_TASK_FAILURE | Task: {task_id} | Trace: {trace_id} | Error: {str(e)}")
            
            await self.publisher.publish_event(
                topic=f"chatbuddy.events.{session_id}.failed",
                payload={
                    "task_id": task_id,
                    "session_id": session_id,
                    "error": str(e),
                    "status": "FAILED",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            raise AppError(
                category=ErrorCategory.INTERNAL,
                trace_id=trace_id,
                error={"code": "CHAT_TASK_EXEC_001", "message": "Background chat task failed."}
            )

    async def archive_chat_session(
        self, 
        session_id: str, 
        trace_id: str
    ) -> None:
        logger.info(f"CHAT_ARCHIVE_START | Session: {session_id} | Trace: {trace_id}")
        
        try:
            state = chat_state_manager.get_state(session_id)
            
            await self.publisher.publish_event(
                topic=f"chatbuddy.events.{session_id}.archived",
                payload={
                    "session_id": session_id,
                    "history": state.history,
                    "metadata": state.values,
                    "status": "ARCHIVED",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            chat_state_manager.cleanup_session(session_id)
            logger.info(f"CHAT_ARCHIVE_SUCCESS | Session: {session_id} | Trace: {trace_id}")
            
        except Exception as e:
            logger.error(f"CHAT_ARCHIVE_FAILURE | Session: {session_id} | Error: {str(e)}")

processor = ChatTaskProcessor()

async def process_chat_message_task(task_data: Dict[str, Any], trace_id: str):
    await processor.process_chat_interaction(task_data, trace_id)

async def maintenance_cleanup_task(trace_id: str):
    logger.info(f"CHAT_MAINTENANCE_START | Trace: {trace_id}")

    pass